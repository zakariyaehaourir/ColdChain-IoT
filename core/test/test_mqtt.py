from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings
import paho.mqtt.client as mqtt

from core.commands.run_mqtt import Command, on_message
from core.dto import SensorReadingDTO
from core.signals import high_temperature_detected


class SensorReadingDTOTests(SimpleTestCase):
    def test_deserializes_temperature_and_humidity(self):
        reading = SensorReadingDTO.from_json(b'{"temp": 7.5, "hum": 61}')

        self.assertEqual(reading, SensorReadingDTO(temp=7.5, hum=61.0))

    def test_rejects_missing_or_non_numeric_measurements(self):
        for payload in (b'{"temp": 7}', b'{"temp": "7", "hum": 61}', b'[]'):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    SensorReadingDTO.from_json(payload)


class MQTTWorkerTests(SimpleTestCase):
    @override_settings(CRITICAL_TEMPERATURE_THRESHOLD=8.0)
    @patch("core.commands.run_mqtt.high_temperature_detected.send")
    def test_on_message_emits_temperature_signal_above_threshold(self, signal_send):
        message = SimpleNamespace(
            topic="test/sensors",
            payload=b'{"temp": 8.5, "hum": 61}',
        )

        with self.assertLogs("core.commands.run_mqtt", level="INFO"):
            on_message(None, None, message)

        signal_send.assert_called_once_with(sender=Command, temperature=8.5)

    @override_settings(CRITICAL_TEMPERATURE_THRESHOLD=8.0)
    @patch("core.commands.run_mqtt.high_temperature_detected.send")
    def test_on_message_does_not_emit_signal_at_threshold(self, signal_send):
        message = SimpleNamespace(
            topic="test/sensors",
            payload=b'{"temp": 8.0, "hum": 61}',
        )

        with self.assertLogs("core.commands.run_mqtt", level="INFO"):
            on_message(None, None, message)

        signal_send.assert_not_called()

    @override_settings(
        MQTT_BROKER_HOST="test-broker",
        MQTT_BROKER_PORT=1883,
        MQTT_TOPIC="test/sensors",
    )
    @patch("core.commands.run_mqtt.mqtt.Client")
    def test_command_connects_subscribes_and_deserializes_messages(self, client_factory):
        client = Mock()
        client.subscribe.return_value = (mqtt.MQTT_ERR_SUCCESS, 1)
        client_factory.return_value = client

        call_command("run_mqtt")

        client.connect.assert_called_once_with("test-broker", 1883, keepalive=60)
        client.loop_forever.assert_called_once_with()
        client.on_connect(client, None, None, Mock(is_failure=False), None)
        client.subscribe.assert_called_once_with("test/sensors")

        message = SimpleNamespace(
            topic="test/sensors",
            payload=b'{"temp": 7.5, "hum": 61}',
        )
        with self.assertLogs("core.commands.run_mqtt", level="INFO") as logs:
            client.on_message(client, None, message)

        self.assertIn("temperature=7.5 C, humidity=61.0%", logs.output[0])

    def test_on_message_logs_invalid_json_without_running_business_logic(self):
        message = SimpleNamespace(topic="test/sensors", payload=b"not-json")

        with self.assertLogs("core.commands.run_mqtt", level="ERROR") as logs:
            on_message(None, None, message)

        self.assertIn("Could not deserialize MQTT message", logs.output[0])

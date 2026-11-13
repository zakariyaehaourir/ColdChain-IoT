import logging
import json
import paho.mqtt.client as mqtt
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.dto import SensorReadingDTO
from core.signals import high_temperature_detected

logger = logging.getLogger(__name__)


def on_message(client, userdata, message):
    try:
        reading = SensorReadingDTO.from_json(message.payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        logger.error(
            "Could not deserialize MQTT message from topic %s: %s",
            message.topic,
            exc,
        )
        return

    logger.info(
        "Deserialized MQTT reading from topic %s: temperature=%.1f C, humidity=%.1f%%",
        message.topic,
        reading.temp,
        reading.hum,
    )
    if reading.temp > settings.CRITICAL_TEMPERATURE_THRESHOLD:
        logger.info(
            "Temperature %.1f C exceeded the critical threshold of %.1f C.",
            reading.temp,
            settings.CRITICAL_TEMPERATURE_THRESHOLD,
        )
        high_temperature_detected.send(
            sender=Command,
            temperature=reading.temp,
        )


class Command(BaseCommand):
    help = "Connect to the configured MQTT broker and deserialize sensor readings."

    def handle(self, *args, **options):
        broker_host = settings.MQTT_BROKER_HOST
        broker_port = settings.MQTT_BROKER_PORT
        topic = settings.MQTT_TOPIC

        if not broker_host:
            raise CommandError("MQTT_BROKER_HOST must be configured.")
        if not topic:
            raise CommandError("MQTT_TOPIC must be configured.")

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        def on_connect(client, userdata, connect_flags, reason_code, properties):
            if reason_code.is_failure:
                logger.error("MQTT connection to %s failed: %s", broker_host, reason_code)
                return

            logger.info("Connected to MQTT broker at %s:%s.", broker_host, broker_port)
            result, _ = client.subscribe(topic)
            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.error("Failed to subscribe to MQTT topic %s.", topic)
                return
            logger.info("Subscribed to MQTT topic %s.", topic)

        client.on_connect = on_connect
        client.on_message = on_message

        logger.info("Connecting to MQTT broker at %s:%s.", broker_host, broker_port)
        try:
            client.connect(broker_host, broker_port, keepalive=60)
            client.loop_forever()
        except (OSError, mqtt.MQTTException) as exc:
            raise CommandError(
                f"MQTT worker failed while connecting to {broker_host}:{broker_port}: {exc}"
            ) from exc

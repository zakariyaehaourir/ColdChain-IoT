from django.test import TestCase
from django.test import override_settings
from django.core import mail
import smtplib
from requests.exceptions import Timeout
from unittest.mock import Mock, patch
from core.models import FridgeSensor


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    TELEGRAM_BOT_TOKEN="test-bot-token",
    TELEGRAM_CHAT_ID="123456789",
)
class SensorEmailAlertTests(TestCase):
    def test_post_sends_email_when_temperature_is_below_25(self):
        telegram_response = Mock()
        telegram_response.json.return_value = {"ok": True}
        telegram_response.raise_for_status.return_value = None
        requests_post = Mock(return_value=telegram_response)

        with patch("core.api.requests.post", requests_post):
            response = self.client.post(
                "/sensors/",
                {"temp": 24.9, "hum": 60.0},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mbch33255@gmail.com"])
        self.assertIn("24.9", mail.outbox[0].body)
        requests_post.assert_called_once_with(
            "https://api.telegram.org/bottest-bot-token/sendMessage",
            json={
                "chat_id": "123456789",
                "text": "Alerte température du réfrigérateur : 24.9 °C, sous le seuil de 25 °C.",
            },
            timeout=10,
        )

    def test_post_does_not_send_email_or_telegram_when_temperature_is_25_or_higher(self):
        with (
            patch("core.api.requests.post") as requests_post,
            self.assertLogs("core.api", level="DEBUG") as captured_logs,
        ):
            for temperature in (25.0, 26.0):
                with self.subTest(temperature=temperature):
                    response = self.client.post(
                        "/sensors/",
                        {"temp": temperature, "hum": 60.0},
                        content_type="application/json",
                    )

                    self.assertEqual(response.status_code, 201)

        self.assertEqual(len(mail.outbox), 0)
        requests_post.assert_not_called()
        self.assertTrue(
            any("No temperature alert" in message for message in captured_logs.output)
        )

    def test_smtp_failure_is_logged_and_telegram_is_still_attempted(self):
        telegram_response = Mock()
        telegram_response.json.return_value = {"ok": True}
        telegram_response.raise_for_status.return_value = None

        with (
            patch("core.api.send_mail", side_effect=smtplib.SMTPException("SMTP unavailable")),
            patch("core.api.requests.post", return_value=telegram_response) as requests_post,
            self.assertLogs("core.api", level="ERROR") as captured_logs,
        ):
            response = self.client.post(
                "/sensors/",
                {"temp": 20.0, "hum": 60.0},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertIn("SMTP alert failed", captured_logs.output[0])
        requests_post.assert_called_once()

    def test_telegram_failure_is_logged_without_failing_sensor_post(self):
        with (
            patch("core.api.requests.post", side_effect=Timeout),
            self.assertLogs("core.api", level="ERROR") as captured_logs,
        ):
            response = self.client.post(
                "/sensors/",
                {"temp": 20.0, "hum": 60.0},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            any("Telegram alert failed" in message for message in captured_logs.output)
        )


class HomeViewTests(TestCase):
    def test_home_view_renders_index_template(self):
        FridgeSensor.objects.create(temp=4.5, hum=62.0)

        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Tableau de bord")
        self.assertContains(response, "Température")
        self.assertContains(response, "Humidité")
        self.assertContains(response, "4.5")
        self.assertContains(response, "62.0")
        self.assertContains(response, 'id="latest-age"')
        self.assertContains(response, 'class="sensor-card sensor-card--latest"')
        self.assertContains(response, 'href="/history/"')

    def test_home_view_shows_empty_state_when_there_are_no_sensors(self):
        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune mesure disponible.")

    def test_history_view_shows_all_measurements_in_reverse_chronological_order(self):
        older_sensor = FridgeSensor.objects.create(temp=3.0, hum=55.0)
        newer_sensor = FridgeSensor.objects.create(temp=4.5, hum=62.0)

        response = self.client.get("/history/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "history.html")
        self.assertContains(response, "Historique des mesures")
        self.assertContains(response, 'aria-label="Fil d’Ariane"')
        self.assertContains(response, "55.0")
        self.assertContains(response, "62.0")
        self.assertLess(
            response.content.index(str(newer_sensor.temp).encode()),
            response.content.index(str(older_sensor.temp).encode()),
        )

    def test_history_view_shows_empty_state_when_there_are_no_sensors(self):
        response = self.client.get("/history/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune mesure disponible.")

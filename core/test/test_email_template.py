from django.core import mail
from django.test import TestCase, override_settings

from core.services.alerts.email_strategy import EmailAlertStrategy


class StaticEmailProvider:
    def get_operator_emails(self):
        return ["operator@example.com"]


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="alerts@example.com",
    CRITICAL_TEMPERATURE_THRESHOLD=30.0,
)
class EmailAlertTemplateTests(TestCase):
    def test_strategy_sends_rendered_html_and_plain_text_alternative(self):
        strategy = EmailAlertStrategy(StaticEmailProvider())

        strategy.sendAlert(36.5)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Critical Alert: High Temperature Detected!")
        self.assertEqual(message.from_email, "alerts@example.com")
        self.assertEqual(message.to, ["operator@example.com"])
        self.assertIn("36.5°C", message.body)
        self.assertEqual(len(message.alternatives), 1)

        html_message, content_type = message.alternatives[0]
        self.assertEqual(content_type, "text/html")
        self.assertIn("36.5°C", html_message)
        self.assertIn("30.0°C", html_message)
        self.assertIn('src="cid:coldchain-banner"', html_message)
        self.assertEqual(len(message.attachments), 1)
        self.assertEqual(message.attachments[0].get_content_type(), "image/png")
        self.assertEqual(
            message.attachments[0].get("Content-ID"),
            "<coldchain-banner>",
        )
        self.assertNotIn("{{", html_message)
        self.assertNotIn("tailwind_css", html_message)

    def test_dashboard_uses_web_logo_and_favicon(self):
        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "core/img/coldchain-logo-horizontal-light-bg.svg")
        self.assertContains(response, 'href="/static/core/img/favicon.svg"')

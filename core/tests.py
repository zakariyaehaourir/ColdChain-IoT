from django.test import TestCase
from core.models import FridgeSensor


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

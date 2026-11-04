from django.test import TestCase
from core.models import FridgeSensor


class HomeViewTests(TestCase):
    def test_home_view_renders_index_template(self):
        FridgeSensor.objects.create(temp=4.5, hum=62.0)

        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Fridge Data")
        self.assertContains(response, "Température")
        self.assertContains(response, "4.5")
        self.assertContains(response, "62.0")
        self.assertContains(response, "Dernière donnée reçue")

    def test_home_view_shows_empty_state_when_there_are_no_sensors(self):
        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune mesure disponible.")

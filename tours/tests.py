from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from tours.models import Category, Enquiry, Tour, TourDate


class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(
            name="Domestic Tours",
            slug="group-domestic",
            kind=Category.KIND_GROUP,
        )
        cls.tour = Tour.objects.create(
            category=cls.cat,
            title="Statue Of Unity (2N)",
            slug="statue-of-unity-2n",
            destination="Gujarat",
            duration_label="2N",
            short_description="Sample tour",
            itinerary="<p>Day 1</p>",
            is_featured=True,
            is_published=True,
        )
        TourDate.objects.create(
            tour=cls.tour,
            start_date=date.today() + timedelta(days=30),
            price="12500.00",
            seats=20,
        )

    def test_home_page(self):
        response = self.client.get(reverse("tours:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harmony Tours")
        self.assertContains(response, "Statue Of Unity")

    def test_category_and_detail(self):
        list_resp = self.client.get(reverse("tours:category", args=["group-domestic"]))
        self.assertEqual(list_resp.status_code, 200)
        detail = self.client.get(self.tour.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Tour Dates")

    def test_enquiry_creates_record(self):
        response = self.client.post(
            self.tour.get_absolute_url(),
            {
                "name": "Test Guest",
                "email": "guest@example.com",
                "mobile": "9999999999",
                "city": "Thane",
                "adults": 2,
                "children_5_12": 0,
                "children_below_5": 0,
                "message": "Please share dates",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enquiry.objects.count(), 1)
        self.assertEqual(Enquiry.objects.first().tour, self.tour)

    def test_admin_tour_and_dates(self):
        User = get_user_model()
        User.objects.create_superuser("admin", "a@example.com", "pass12345")
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(reverse("admin:tours_tour_change", args=[self.tour.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tour dates")
        add_resp = self.client.get(reverse("admin:tours_tour_add"))
        self.assertEqual(add_resp.status_code, 200)
        self.assertContains(add_resp, "start_date")

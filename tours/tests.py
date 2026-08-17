from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from tours.models import Category, Enquiry, Invoice, InvoiceLine, Tour, TourDate


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


class InvoiceTests(TestCase):
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
            is_published=True,
        )
        cls.user = get_user_model().objects.create_superuser(
            "admin", "a@example.com", "pass12345"
        )

    def test_invoice_number_and_gst_totals(self):
        invoice = Invoice.objects.create(
            customer_name="Test Guest",
            tour=self.tour,
            gst_percent="5.00",
        )
        self.assertTrue(invoice.number.startswith("HT-"))
        InvoiceLine.objects.create(
            invoice=invoice,
            description="Package — 2 adults",
            quantity=2,
            unit_price="10000.00",
        )
        invoice.refresh_from_db()
        self.assertEqual(str(invoice.subtotal), "20000.00")
        self.assertEqual(str(invoice.gst_amount), "1000.00")
        self.assertEqual(str(invoice.total), "21000.00")

    def test_print_requires_staff(self):
        invoice = Invoice.objects.create(customer_name="Guest")
        url = reverse("tours:invoice_print", args=[invoice.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, invoice.number)

    def test_admin_invoice_form(self):
        self.client.login(username="admin", password="pass12345")
        response = self.client.get(reverse("admin:tours_invoice_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invoice lines")

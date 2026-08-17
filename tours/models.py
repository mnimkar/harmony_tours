from decimal import Decimal, ROUND_HALF_UP

from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    KIND_GROUP = "group"
    KIND_INDIVIDUAL = "individual"
    KIND_SPECIALISED = "specialised"
    KIND_CHOICES = [
        (KIND_GROUP, "Group Tours"),
        (KIND_INDIVIDUAL, "Individual Tours"),
        (KIND_SPECIALISED, "Specialised Tours"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["kind", "sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.get_kind_display()} / {self.name}"

    def get_absolute_url(self):
        return reverse("tours:category", args=[self.slug])


class Tour(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="tours"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    destination = models.CharField(max_length=120, blank=True)
    duration_label = models.CharField(
        max_length=80,
        blank=True,
        help_text="Shown on cards, e.g. 07 N / 08 D",
    )
    nights = models.PositiveSmallIntegerField(null=True, blank=True)
    short_description = models.TextField(blank=True)
    itinerary = models.TextField(blank=True, help_text="Day-wise itinerary (plain text or HTML)")
    cost_includes = models.TextField(blank=True)
    cost_excludes = models.TextField(blank=True)
    offers = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to="tours/", blank=True)
    is_featured = models.BooleanField(
        default=False, help_text="Show in homepage Available Tours"
    )
    is_latest_excursion = models.BooleanField(
        default=False, help_text="Show in homepage Latest Excursion"
    )
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:detail", args=[self.category.slug, self.slug])

    def upcoming_dates(self):
        today = timezone.localdate()
        return self.dates.filter(is_active=True, start_date__gte=today).order_by(
            "start_date"
        )

    def all_active_dates(self):
        return self.dates.filter(is_active=True).order_by("start_date")


class TourDate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="dates")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Optional per-person price",
    )
    seats = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Seats remaining (optional)"
    )
    notes = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_date"]
        verbose_name = "Tour date"
        verbose_name_plural = "Tour dates"

    def __str__(self):
        label = self.start_date.strftime("%d %b %Y")
        if self.end_date:
            label += f" – {self.end_date.strftime('%d %b %Y')}"
        return f"{self.tour.title}: {label}"


class Banner(models.Model):
    title = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="banners/")
    link = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title or f"Banner {self.pk}"


class Enquiry(models.Model):
    tour = models.ForeignKey(
        Tour, null=True, blank=True, on_delete=models.SET_NULL, related_name="enquiries"
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    city = models.CharField(max_length=80, blank=True)
    adults = models.PositiveSmallIntegerField(default=1)
    children_5_12 = models.PositiveSmallIntegerField(default=0)
    children_below_5 = models.PositiveSmallIntegerField(default=0)
    travel_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Enquiries"

    def __str__(self):
        target = self.tour.title if self.tour else "General"
        return f"{self.name} — {target}"


def _money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Invoice(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_ISSUED = "issued"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ISSUED, "Issued"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    number = models.CharField(max_length=32, unique=True, blank=True, editable=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)

    tour = models.ForeignKey(
        Tour, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices"
    )
    tour_date = models.ForeignKey(
        TourDate, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices"
    )
    enquiry = models.ForeignKey(
        Enquiry, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices"
    )

    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField(blank=True)
    customer_mobile = models.CharField(max_length=20, blank=True)
    customer_city = models.CharField(max_length=80, blank=True)
    customer_address = models.TextField(blank=True)
    customer_gstin = models.CharField(max_length=15, blank=True)

    gst_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("5.00"),
        help_text="GST on package cost (site currently uses 5%)",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def __str__(self):
        return self.number or f"Draft invoice for {self.customer_name}"

    def get_absolute_url(self):
        return reverse("tours:invoice_print", args=[self.pk])

    @classmethod
    def next_number(cls, issue_date=None):
        year = (issue_date or timezone.localdate()).year
        prefix = f"HT-{year}-"
        last = (
            cls.objects.filter(number__startswith=prefix)
            .order_by("-number")
            .values_list("number", flat=True)
            .first()
        )
        seq = int(last.split("-")[-1]) + 1 if last else 1
        return f"{prefix}{seq:04d}"

    def recalculate(self, save=True):
        subtotal = sum((line.amount for line in self.lines.all()), Decimal("0.00"))
        self.subtotal = _money(subtotal)
        rate = _money(self.gst_percent or 0)
        self.gst_amount = _money(Decimal(self.subtotal) * rate / Decimal("100"))
        self.total = _money(Decimal(self.subtotal) + Decimal(self.gst_amount))
        if save:
            self.save(update_fields=["subtotal", "gst_amount", "total", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.number:
            with transaction.atomic():
                self.number = self.next_number(self.issue_date)
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.description

    @property
    def amount(self):
        return _money(Decimal(self.quantity) * Decimal(self.unit_price))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.recalculate()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.recalculate()

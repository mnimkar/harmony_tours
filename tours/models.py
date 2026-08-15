from django.db import models
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

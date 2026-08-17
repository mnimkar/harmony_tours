from decimal import Decimal

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import Banner, Category, Enquiry, Invoice, InvoiceLine, Tour, TourDate


class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 3
    fields = ("start_date", "end_date", "price", "seats", "notes", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "slug", "sort_order", "tour_count")
    list_filter = ("kind",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def tour_count(self, obj):
        return obj.tours.count()

    tour_count.short_description = "Tours"


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "thumb",
        "title",
        "category",
        "destination",
        "duration_label",
        "upcoming_count",
        "is_featured",
        "is_published",
        "sort_order",
    )
    list_display_links = ("thumb", "title")
    list_filter = ("category", "is_published", "is_featured", "destination")
    search_fields = ("title", "destination", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TourDateInline]
    fieldsets = (
        (
            "Listing",
            {
                "fields": (
                    "category",
                    "title",
                    "slug",
                    "destination",
                    "duration_label",
                    "nights",
                    "image",
                    "short_description",
                    "is_featured",
                    "is_latest_excursion",
                    "is_published",
                    "sort_order",
                )
            },
        ),
        (
            "Tour details (shown on tour page tabs)",
            {
                "fields": (
                    "itinerary",
                    "cost_includes",
                    "cost_excludes",
                    "offers",
                    "notes",
                )
            },
        ),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:64px;object-fit:cover;border-radius:3px;" />',
                obj.image.url,
            )
        return "—"

    thumb.short_description = ""

    def upcoming_count(self, obj):
        return obj.upcoming_dates().count()

    upcoming_count.short_description = "Upcoming dates"


@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ("tour", "start_date", "end_date", "price", "seats", "is_active")
    list_filter = ("is_active", "start_date", "tour__category")
    search_fields = ("tour__title", "notes")
    autocomplete_fields = ("tour",)
    date_hierarchy = "start_date"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tour",
        "email",
        "mobile",
        "city",
        "adults",
        "travel_date",
        "created_at",
    )
    list_filter = ("created_at", "tour")
    search_fields = ("name", "email", "mobile", "city")
    readonly_fields = (
        "tour",
        "name",
        "email",
        "mobile",
        "city",
        "adults",
        "children_5_12",
        "children_below_5",
        "travel_date",
        "message",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    actions = ["create_invoice"]

    @admin.action(description="Create invoice from selected enquiries")
    def create_invoice(self, request, queryset):
        created = 0
        for enquiry in queryset:
            invoice = Invoice.objects.create(
                enquiry=enquiry,
                tour=enquiry.tour,
                customer_name=enquiry.name,
                customer_email=enquiry.email,
                customer_mobile=enquiry.mobile,
                customer_city=enquiry.city,
                notes=enquiry.message,
            )
            qty = enquiry.adults or 1
            unit = Decimal("0.00")
            description = enquiry.tour.title if enquiry.tour else "Tour package"
            if enquiry.tour:
                priced = enquiry.tour.dates.filter(price__isnull=False).order_by("start_date").first()
                if priced and priced.price:
                    unit = priced.price
            InvoiceLine.objects.create(
                invoice=invoice,
                description=description,
                quantity=qty,
                unit_price=unit,
            )
            created += 1
        self.message_user(
            request,
            f"Created {created} invoice(s). Open Invoices to add line items and print.",
            messages.SUCCESS,
        )


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    fields = ("description", "quantity", "unit_price")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "customer_name",
        "tour",
        "issue_date",
        "status",
        "total",
        "print_link",
    )
    list_filter = ("status", "issue_date")
    search_fields = ("number", "customer_name", "customer_email", "customer_mobile")
    autocomplete_fields = ("tour", "tour_date", "enquiry")
    readonly_fields = ("number", "subtotal", "gst_amount", "total", "created_at", "updated_at")
    inlines = [InvoiceLineInline]
    date_hierarchy = "issue_date"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "number",
                    "status",
                    "issue_date",
                    "due_date",
                    "paid_date",
                    "tour",
                    "tour_date",
                    "enquiry",
                )
            },
        ),
        (
            "Bill to",
            {
                "fields": (
                    "customer_name",
                    "customer_email",
                    "customer_mobile",
                    "customer_city",
                    "customer_address",
                    "customer_gstin",
                )
            },
        ),
        (
            "Totals",
            {"fields": ("gst_percent", "subtotal", "gst_amount", "total", "notes")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def print_link(self, obj):
        if not obj.pk:
            return "—"
        url = reverse("tours:invoice_print", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Print</a>', url)

    print_link.short_description = "Invoice"

    def response_change(self, request, obj):
        if "_print" in request.POST:
            return redirect(obj.get_absolute_url())
        return super().response_change(request, obj)

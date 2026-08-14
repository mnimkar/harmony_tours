from django.contrib import admin
from django.utils.html import format_html

from .models import Banner, Category, Enquiry, Tour, TourDate


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

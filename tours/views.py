from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EnquiryForm
from .models import Banner, Category, Tour


def home(request):
    featured = Tour.objects.filter(is_published=True, is_featured=True)
    latest = Tour.objects.filter(is_published=True, is_latest_excursion=True)
    banners = Banner.objects.filter(is_active=True)
    return render(
        request,
        "tours/home.html",
        {
            "featured_tours": featured,
            "latest_excursions": latest,
            "banners": banners,
        },
    )


def about(request):
    return render(request, "tours/about.html")


def contact(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you. We will get in touch shortly.")
            return redirect("tours:contact")
    else:
        form = EnquiryForm()
    return render(request, "tours/contact.html", {"form": form})


def educational(request):
    return render(request, "tours/educational.html")


def inspirational(request):
    return render(request, "tours/inspirational.html")


def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    tours = category.tours.filter(is_published=True)
    siblings = Category.objects.filter(kind=category.kind)
    destinations = (
        tours.exclude(destination="")
        .values_list("destination", flat=True)
        .distinct()
        .order_by("destination")
    )
    return render(
        request,
        "tours/category.html",
        {
            "category": category,
            "tours": tours,
            "siblings": siblings,
            "destinations": destinations,
        },
    )


@require_http_methods(["GET", "POST"])
def tour_detail(request, category_slug, tour_slug):
    tour = get_object_or_404(
        Tour.objects.select_related("category"),
        category__slug=category_slug,
        slug=tour_slug,
        is_published=True,
    )
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.tour = tour
            enquiry.save()
            messages.success(request, "Thank you. We will get in touch shortly.")
            return redirect(tour.get_absolute_url())
    else:
        form = EnquiryForm()
    similar = (
        Tour.objects.filter(is_published=True, category=tour.category)
        .exclude(pk=tour.pk)[:6]
    )
    siblings = Category.objects.filter(kind=tour.category.kind)
    return render(
        request,
        "tours/detail.html",
        {
            "tour": tour,
            "form": form,
            "similar": similar,
            "siblings": siblings,
            "dates": tour.all_active_dates(),
        },
    )

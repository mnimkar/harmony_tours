from django.urls import path

from . import views

app_name = "tours"

urlpatterns = [
    path("", views.home, name="home"),
    path("Home/", views.home, name="home_alias"),
    path("About-Us/", views.about, name="about"),
    path("Contact/", views.contact, name="contact"),
    path("Educational-Tours/", views.educational, name="educational"),
    path("Inspirational-Tourism/", views.inspirational, name="inspirational"),
    path("tours/<slug:category_slug>/", views.category_detail, name="category"),
    path(
        "tours/<slug:category_slug>/<slug:tour_slug>/",
        views.tour_detail,
        name="detail",
    ),
    path("invoices/<int:pk>/", views.invoice_print, name="invoice_print"),
]

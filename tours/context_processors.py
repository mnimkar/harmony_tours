from django.conf import settings

from .models import Category


def site_nav(request):
    categories = Category.objects.all()
    grouped = {
        "group": [c for c in categories if c.kind == Category.KIND_GROUP],
        "individual": [c for c in categories if c.kind == Category.KIND_INDIVIDUAL],
        "specialised": [c for c in categories if c.kind == Category.KIND_SPECIALISED],
    }
    return {
        "site_name": settings.SITE_NAME,
        "site_phone_primary": settings.SITE_PHONE_PRIMARY,
        "site_phone_secondary": settings.SITE_PHONE_SECONDARY,
        "site_email": settings.SITE_EMAIL,
        "site_address": settings.SITE_ADDRESS,
        "facebook_url": settings.FACEBOOK_URL,
        "instagram_url": settings.INSTAGRAM_URL,
        "nav_categories": grouped,
    }

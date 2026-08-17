from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Harmony Tours Admin"
admin.site.site_title = "Harmony Tours"
admin.site.index_title = "Manage tours, dates and enquiries"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tours.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import include, path

from .views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("clients/", include("clients.urls")),
    path("deals/", include("deals.urls")),
    path("tasks/", include("tasks.urls")),
    path("", DashboardView.as_view(), name="dashboard"),
]
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from clients.api import ClientViewSet, InteractionViewSet
from deals.api import DealViewSet
from tasks.api import TaskViewSet

from .views import DashboardView

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="api-clients")
router.register("interactions", InteractionViewSet, basename="api-interactions")
router.register("deals", DealViewSet, basename="api-deals")
router.register("tasks", TaskViewSet, basename="api-tasks")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("clients/", include("clients.urls")),
    path("deals/", include("deals.urls")),
    path("tasks/", include("tasks.urls")),
    path("api/", include(router.urls)),
    path("api/token/", obtain_auth_token, name="api-token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path("api-auth/", include("rest_framework.urls")),
    path("", DashboardView.as_view(), name="dashboard"),
]
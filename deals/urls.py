from django.urls import path

from . import views

app_name = "deals"

urlpatterns = [
    path("", views.DealBoardView.as_view(), name="board"),
    path("new/", views.DealCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.DealUpdateView.as_view(), name="update"),
    path("<int:pk>/stage/", views.DealStageView.as_view(), name="stage"),
]
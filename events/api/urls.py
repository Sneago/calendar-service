from django.urls import path

from events.api import views

app_name = "events"

urlpatterns = [
    path("add/", views.EventCreateView.as_view(), name="add"),
    path(
        "events/<int:year>/<int:month>/<int:day>/",
        views.EventListView.as_view(),
        name="events",
    ),
]

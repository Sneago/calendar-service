from django.urls import path

from events.api import views

app_name = "events"

urlpatterns = [
    path("add/", views.EventCreateView.as_view(), name="add"),
    path(
        "remove/<int:pk>/<int:year>/<int:month>/<int:day>/",
        views.OccurrenceCancelView.as_view(),
        name="remove",
    ),
    path(
        "update/<int:pk>/<int:year>/<int:month>/<int:day>/",
        views.OccurrenceRenameView.as_view(),
        name="update",
    ),
    path(
        "events/<int:year>/<int:month>/<int:day>/",
        views.EventListView.as_view(),
        name="events",
    ),
]

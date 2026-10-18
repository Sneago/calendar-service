from django.urls import path, register_converter

from events.api import views
from events.api.converters import DateConverter

register_converter(DateConverter, "date")

app_name = "events"

urlpatterns = [
    path("add/", views.EventCreateView.as_view(), name="add"),
    path("events/<date:day>/", views.EventListView.as_view(), name="events"),
]

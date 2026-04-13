from django.urls import path
from . import views

app_name = "quests"

urlpatterns = [
    path("today/complete/", views.complete_today, name="complete_today"),
    path("today/skip/", views.skip_today, name="skip_today"),
]

from django.urls import path

from . import views


app_name = "src"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "notes/<int:note_id>/",
        views.insecure_note_detail,
        name="insecure-note-detail",
    ),
    path("credentials/", views.insecure_credentials, name="insecure-credentials"),
    path("injection/search/", views.insecure_search, name="insecure-search"),
    path("authentication/login/", views.insecure_login, name="insecure-login"),
]

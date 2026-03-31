from django.urls import path
from .views import index, check_refs

urlpatterns = [
    path("", index, name="index"),
    path("check_refs/", check_refs, name="check_refs"),
]
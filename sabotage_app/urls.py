# mytodo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("course/create/", views.course_create, name="course_create"),
    path("course/<int:course_id>/edit/", views.course_edit, name="course_edit"),
    path("course/<int:course_id>/delete/", views.course_delete, name="course_delete"),
    path("sabotage-record/edit/", views.sabotage_record_edit, name="sabotage_record_edit"),
]
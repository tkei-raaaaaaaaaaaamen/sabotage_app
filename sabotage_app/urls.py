# mytodo/urls.py
from django.urls import path
from sabotage_app import views as sabotage_app

urlpatterns = [
    path("", sabotage_app.index, name="index"),
    path("login/", sabotage_app.login_view, name="login"),
    path("logout/", sabotage_app.logout_view, name="logout"),
    path("signup/", sabotage_app.signup_view, name="signup"),
    path("add-absence/", sabotage_app.add_absence_view, name="add_absence"),
    path("course/<int:course_id>/", sabotage_app.course_detail_view, name="course_detail"),
    path("course/create/", sabotage_app.course_create_view, name="course_create"),
    path("course/<int:course_id>/edit/", sabotage_app.course_edit_view, name="course_edit"),
    path("course/<int:course_id>/delete/", sabotage_app.course_delete_view, name="course_delete"),
    path("record/<int:record_id>/edit/", sabotage_app.record_edit_view, name="record_edit"),
    path("record/<int:record_id>/delete/", sabotage_app.record_delete_view, name="record_delete"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("myquestions", views.myquestions, name="myquestions"),
    path("papergen1", views.papergen1, name="papergen1"),
    path("papergen2", views.papergen2, name="papergen2"),
    path("mypapers", views.mypapers, name="mypapers"),
    path('search/<str:query>', views.search, name='search'),
]
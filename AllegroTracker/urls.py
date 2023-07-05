from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import verification_view
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_product", views.add_product, name="add_product"),
    path("edit_product/<int:product_id>", views.edit_product, name="edit_product"),
    path("delete_product/<int:product_id>", views.delete_product, name="delete_product"),
    path("search_product", csrf_exempt(views.search_product), name="search_product"),
    path("register", views.register, name="register"),
    path("product_details/<int:product_id>", views.product_details, name="product_details"),
    path("activate/<uidb64>/<token>", verification_view.as_view(), name="activate"),
]

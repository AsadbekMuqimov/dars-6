from django.urls import path
from . import views

urlpatterns = [
    path('mycart/', views.mycart, name='mycart'),
    path('create_order/', views.create_order, name='create_order'),
    path('addProductToCart/', views.addProductToCart, name='addproducttocart'),
    path('subtract_from_cart/', views.subtract_from_cart, name='subtract_from_cart'),
    path('delete_from_cart/', views.delete_from_cart, name='delete_from_cart'),
]

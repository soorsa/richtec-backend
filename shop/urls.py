from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter(trailing_slash=False)
router.register(r'products', views.ProductApiSet, basename='products')
router.register(r'categories', views.CategoryApiSet, basename='categories')
router.register(r'orders', views.OrderApiSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', views.Checkout.as_view(), name='checkout'),
    path('report/', views.DashboardReportView.as_view(), name='report'),

]

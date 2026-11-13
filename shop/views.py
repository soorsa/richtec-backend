from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, Q

# Create your views here.
class ProductApiSet(viewsets.ModelViewSet):
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    lookup_field = "slug"
    filterset_fields = ["title", "category__slug", "price"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "create_at", "price"]
    def get_queryset(self):
        user = self.request.user
        # Check if the user is authenticated and is staff (or a superuser)
        if user and user.is_authenticated and user.is_staff:
            return Product.objects.all()
        
        # Otherwise, only return active products for regular users or guests
        return Product.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.action in ["list", "retrieve",]:
            return [AllowAny()]
        return [IsAuthenticated(),IsAdminUser()]
    
class CategoryApiSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    lookup_field = "slug"
    filterset_fields = ["title"]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve",]:
            return [AllowAny()]
        return [IsAuthenticated(),IsAdminUser()]
    
class OrderApiSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    lookup_field = "id"
    # filterset_fields = [""]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve",]:
            return [AllowAny()]
        return [IsAuthenticated(),IsAdminUser()]
    
class Checkout(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]


class DashboardReportView(APIView):
    """
    API view to return summary statistics for dashboard reporting.
    """
    def get(self, request, *args, **kwargs):
        # 1. Product Metrics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        total_products_value = Product.objects.aggregate(total_volume=Sum('price'))['total_volume'] or 0.00

        # 2. Order Status Breakdown
        order_counts = Order.objects.aggregate(
            total_orders=Count('id'),
            pending_orders=Count('id', filter=Q(status='Pending')),
            confirmed_orders=Count('id', filter=Q(status='Confirmed')),
            on_route_orders=Count('id', filter=Q(status='On-route')),
            delivered_orders=Count('id', filter=Q(status='Delivered')),
            completed_orders=Count('id', filter=Q(status='Completed')),
            canceled_orders=Count('id', filter=Q(status='Canceled')),
        )

        # 3. Sales & Revenue Calculations
        # Total Sales: Total number of orders that are completed/successful 
        # Revenue: Sum of the 'total' field where payment is received or order is completed/delivered
        revenue_stats = Order.objects.filter(
            Q(payment_received=True) | Q(status__in=['Completed', 'Delivered'])
        ).aggregate(
            total_revenue=Sum('total'),
            total_sales_count=Count('id')
        )

        # Overall gross volume (sum of all orders regardless of status)
        gross_volume = Order.objects.aggregate(total_volume=Sum('total'))['total_volume'] or 0.00

        data = {
            "products": {
                "total_products": total_products,
                "active_products": active_products,
                "total_products_value": total_products_value,
            },
            "orders": {
                "total_orders": order_counts['total_orders'],
                "pending": order_counts['pending_orders'],
                "confirmed": order_counts['confirmed_orders'],
                "on_route": order_counts['on_route_orders'],
                "delivered": order_counts['delivered_orders'],
                "completed": order_counts['completed_orders'],
                "canceled": order_counts['canceled_orders'],
            },
            "financials": {
                "total_revenue": revenue_stats['total_revenue'] or 0.00,
                "paid_sales_count": revenue_stats['total_sales_count'] or 0,
                "gross_order_volume": gross_volume,
            }
        }

        return Response(data, status=status.HTTP_200_OK)
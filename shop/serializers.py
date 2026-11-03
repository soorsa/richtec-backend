from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','slug', 'thumbnail', 'is_featured', 'total_products']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image',]


class ProductSerializer(serializers.ModelSerializer):
    # For reading (GET requests): returns the full category object
    category = CategorySerializer(read_only=True)
    
    # For writing (POST/PUT/PATCH requests): accepts the category's slug string
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        source='category', # Maps this input directly to the 'category' model field
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'category_slug', 'tag', 'price', 'description',
            'features', 'thumbnail', 'images', 'uploaded_images',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        files = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        for i, f in enumerate(files):
            ProductImage.objects.create(product=product, image=f)
        return product     


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'amount']  # Adjust fields based on your actual OrderItem model
        read_only_fields = ['id']
class OrderItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        depth = 2
        fields = ['id', 'product', 'quantity', 'amount']  # Adjust fields based on your actual OrderItem model
        read_only_fields = ['id']

class OrderSerializer(serializers.ModelSerializer):
    # Optional: If you want to accept or return items nested within the order creation
    order_items = OrderItemSerializer(many=True, write_only=True, required=True)
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'phone_number', 'alt_phone_number', 'email',
            'total', 'country', 'state', 'town', 'address', 'note',
            'payment_received', 'payment_method', 'status', 'order_date', 'order_items', 'items', 'total_items'
        ]
        read_only_fields = ['id', 'order_date', 'status', 'payment_received', 'items']

    def validate_order_items(self, value):
            """
            Check that the order_items list is not empty.
            """
            if not value or len(value) == 0:
                raise serializers.ValidationError("An order must contain at least one item.")
            return value

    def create(self, validated_data):
        items_data = validated_data.pop('order_items', [])
        # Create the order instance
        order = Order.objects.create(**validated_data)
        
        # Create associated order items if your checkout payload provides them
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order


# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = "__all__"
        # fields = ['id']

    # def create(self, validated_data):
    #     files = validated_data.pop('uploaded_images', [])
    #     product = Product.objects.create(**validated_data)
    #     for i, f in enumerate(files):
    #         ProductImage.objects.create(product=product, image=f)
    #     return product        


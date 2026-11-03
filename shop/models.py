from django.db import models
from django.utils.text import slugify
import uuid

ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('On-route', 'On-route'),
    ('Delivered', 'Delivered'),
    ('Canceled', 'Canceled'),
    ('Completed', 'Completed'),
)
TAGS = (
    ('best seller','best seller'),
    ('hot', 'hot'),
    ('trending', 'trending'),
    ('new arrival', 'new arrival'),
)

PAYMENT_METHOD = (
    ('Paystack', 'Paystack'),
    ('Pay on Delivery', 'Pay on Delivery'),
    ('Bank Transfer', 'Bank Transfer'),
)


class Category(models.Model):
    """Model definition for Category."""

    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='category_thumbnails', blank=True, null=True, default='cat_thumbnail.png')
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_products(self):
        products = self.products.all()
        return products.count()

    def __str__(self):
        return self.title


class Product(models.Model):
    """Model definition for Product."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    tag = models.CharField(
        choices=TAGS,
        # default="Pending",
        max_length=50,
        blank=True,
        null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    
    # Store features as a JSON array (e.g. ["Feature 1", "Feature 2"])
    features = models.JSONField(default=list, blank=True)
    thumbnail = models.ImageField(upload_to='product_thumbnail', blank=True, null=True, default='product.jpg')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = self._unique_slug(slugify(self.title))
        super().save(*args, **kwargs)

    def _unique_slug(self, base):
        slug = base or "item"
        Model = type(self)
        i = 1
        # Only exclude yourself (matters on update)
        qs = Model.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            i += 1
            slug = f"{base}-{i}"
            qs = Model.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
        return slug
    
    def __str__(self):
        return self.title or f"Product #{self.id}"

class ProductImage(models.Model):
    """Allows multiple secondary gallery images per product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_img')

    def __str__(self):
        return f"Image for {self.product.title}"
    
class Order(models.Model):
    """Model definition for Order."""

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alt_phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_received = models.BooleanField(default=False)
    payment_method = models.CharField(
        default="Pay on Delivery",
        choices=PAYMENT_METHOD,
        max_length=100,
        blank=True,
        null=True
    )
    status = models.CharField(
        choices=ORDER_STATUS,
        default="Pending",
        max_length=50,
        blank=True,
        null=True
    )
    order_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_items(self):
        order_items = self.items.all()
        value = sum([item.quantity for item in order_items])
        return value

    def __str__(self):
        return f'Order {self.id} - {self.customer_name}'


class OrderItem(models.Model):
    """Join model tracking ordered products with quantity and price snapshot."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def amount(self):
        total = self.product.price * self.quantity
        return total
     
    def __str__(self):
        return f"{self.quantity}x {self.product.title if self.product else 'Deleted Product'}"
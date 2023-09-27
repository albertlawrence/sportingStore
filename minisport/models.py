from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.username

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('cricket', 'Cricket'),
        ('football', 'Football'),
        ('tennis', 'Tennis'),
        # Add more category choices as needed
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='cricket')
    name = models.CharField(max_length=255, null=True)
    size = models.CharField(max_length=50, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True)
    approved = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    product_count = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.name

    def get_available_products(self):
        # Define product options for each category
        product_options = {
            'cricket': ['Cricket Ball', 'Cricket Bat', 'Cricket Jersey', 'Cricket Shoes'],
            'football': ['Football', 'Jersey', 'Boot'],
            'tennis': ['Tennis Ball', 'Tennis Bat', 'Tennis Shoes'],
            # Add more categories and products as needed
        }

        # Return available products based on the category of the product
        return product_options.get(self.category, [])

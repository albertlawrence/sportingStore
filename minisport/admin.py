from django.contrib import admin
from .models import UserProfile,Product

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Product)
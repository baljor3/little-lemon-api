from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(MenuItems)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(order)
admin.site.register(orderItem)
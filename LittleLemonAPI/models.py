from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length =255, db_index = True)

    def __str__(self):
        return self.title

class MenuItems(models.Model):
    name = models.CharField(max_length =225)
    price = models.DecimalField(max_digits = 6, decimal_places = 2, db_index = True)
    featured =models.BooleanField(db_index = True)
    category = models.ForeignKey(Category, on_delete = models.PROTECT)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        unique_together = ('menuitem','user')

class order(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="deliverycrew", null = True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6,decimal_places=2)
    date =models.DateField(db_index=True)


class orderItem(models.Model):
    order = models.ForeignKey(order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItems, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order','menuitem')

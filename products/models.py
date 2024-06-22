from django.db import models

# Create your models here.

class Category(models.Model):
    title = models.CharField('title', max_length=150)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField('title', max_length=150)
    is_active = models.BooleanField('active', default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

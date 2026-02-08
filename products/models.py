from django.db import models

from django.db import models



class Category(models.Model):
    title=models.CharField(max_length=100)
    image=models.ImageField(upload_to='category_image/', null=True, blank=True)

    def __str__(self):
        return self.title



class Product(models.Model):
    category=models.ForeignKey(Category, on_delete=models.CASCADE,related_name='products')
    title=models.CharField(max_length=100)
    brand=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    discount_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precent=models.IntegerField()
    main_image=models.ImageField(upload_to='product_images/',null=True,blank=True)
    desc=models.TextField()
    stock=models.IntegerField()


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.price and self.precent:
            self.discount_price = self.price - (self.price * self.precent / 100)
        super().save(*args, **kwargs)



class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE ,related_name='image')
    image=models.ImageField(upload_to='product_images',null=True, blank=True)

    def __str__(self):
        return self.product.title


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Banner sarlavhasi")
    image = models.ImageField(upload_to='banners/', verbose_name="Banner rasmi")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
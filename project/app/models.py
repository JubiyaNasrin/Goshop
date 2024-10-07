from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User  # Import the built-in User model
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    reset_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def generate_reset_token(self):
        self.reset_token = uuid.uuid4()
        self.reset_token_expiry = timezone.now() + timedelta(hours=1)  # Token valid for 1 hour
        self.save()
    
# Signal to create or update UserProfile automatically
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

class Category(models.Model):
    name=models.CharField(max_length=250,unique=True)
    slug=models.SlugField(max_length=250,unique=True)
    description=models.TextField(blank=True)
    image=models.ImageField(upload_to='category',blank=True)
    order = models.PositiveIntegerField(default=0)  # New field for custom ordering

    class Meta:
        ordering = ['order']  # Orders categories by the 'order' field by default

    
    def get_url(self):
        return reverse('app:products_by_category',args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)

class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product', blank=True)
    stock=models.IntegerField()
    available=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    class Meta:
        ordering=('name',)
        verbose_name='product'
        verbose_name_plural='products'

    # def get_url(self):
    #     return reverse('app:proDetail',args=[self.category.slug,self.slug])

    def __str__(self):
        return '{}'.format(self.name)
    
class Cart(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow cart to be associated with a user
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)

    class Meta:
        db_table='Cart'
        ordering=['date_added']

    def __str__(self):
        return '{}'.format(self.cart_id)

class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    active=models.BooleanField(default=True)

    class Meta:
        db_table='CartItem'

    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return '{}'.format(self.product)

    
from django.contrib import admin
from app.models import UserProfile, Category, Product, Cart, CartItem

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')  # Show the 'order' field in the admin listing
    list_editable = ('order',)        # Allow editing the 'order' field in the listing

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','price','stock','available','created','updated']
    list_editable = ['price','stock','available']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20
admin.site.register(Product,ProductAdmin)

admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)




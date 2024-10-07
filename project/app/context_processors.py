from app.models import Category ,Cart,CartItem
from app.views import _cart_id

def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)

def counter(request):
    item_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            # Get the cart using the session-based cart_id
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # Fetch all cart items related to this cart
            cart_items = CartItem.objects.filter(cart=cart, active=True)
            # Count the total quantity of items in the cart
            item_count = sum(item.quantity for item in cart_items)
        except Cart.DoesNotExist:
            item_count = 0
    
    return {'item_count': item_count}   


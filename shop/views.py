from django.shortcuts import render,redirect
from shop.models import Product,Category,Cart,Order,OrderItem
from userpage.models import Address
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages


def allProducts(request):
    prod_list = Product.objects.all()
    paginator = Paginator(prod_list, 6) 

    page = request.GET.get('page')
    try:
        prod = paginator.page(page)
    except PageNotAnInteger:
        prod = paginator.page(1)
    except EmptyPage:
        prod = paginator.page(paginator.num_pages)

    categories = Category.objects.filter(is_listed=True)

    context = {
        'prod': prod,
        'categories': categories,
    }
    return render(request, 'allproducts.html', context)

#single product view#
def singleProduct(request,item_id):
    item = Product.objects.get(pk=item_id)
    context = {
        'item':item
    }
    return render(request,'singleproduct.html',context)

#cart view# 
def addtoCart(request, product_id):
    if request.user.is_authenticated:
     product = Product.objects.get(pk=product_id)
     user = request.user

     if request.method == 'POST':
        quantity_str = request.POST.get('quantity', '1')

        if quantity_str.strip():
            quantity = int(quantity_str)
        else:
            quantity = 1
        
        cart_item = Cart.objects.filter(user=user, product=product)

        if cart_item.exists():           
            cart_item = cart_item.first()
            cart_item.quantity += quantity
            cart_item.save()
        else:            
            Cart.objects.create(user=user, product=product, quantity=quantity)
        
        return redirect('viewcart')

    return redirect('login')

def viewCart(request):
    if request.user.is_authenticated:    
        user = request.user
        cart = Cart.objects.filter(user=user)
        total_amount = sum(item.product.price * item.quantity for item in cart)
        context = {'cart':cart,'total_amount':total_amount}

        return render(request, 'cart.html', context)
    return redirect('login')

def deleteCartItem(requst,item_id):
    item = Cart.objects.filter(pk=item_id).delete()
    return redirect('viewcart')

def checkOut(request):    
    user = request.user
    cart = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart)
    addres = Address.objects.filter(user=request.user)
    context = {'cart':cart,
               'total_amount':total_amount,
               'addres':addres}
    if not cart or any(item.quantity < 1 or item.product.stock < 1 for item in cart):
        messages.warning(request, 'No products available Please Shop again.')
        return redirect('viewcart')

    return render(request, 'checkout.html', context)

def addnewAddress(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        hname = request.POST.get('house')        
        phone = request.POST.get('phone')
        post = request.POST.get('place')
        city = request.POST.get('city')
        pincode = request.POST.get('pin')
        state = request.POST.get('state')
        user = request.user
        
        adress = Address.objects.create(user=user,name=name,house_name=hname,phone=phone,post=post,city=city,pin_code=pincode,state=state)
        adress.save()
        return redirect('checkout')
            

    return render(request,'addnewaddress.html')


    
def processOrder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        # Create an order instance and save it to the database
        order = Order.objects.create(user=user, total_price=total_amount, payment_method=payment_method)

        # Create order items for each product in the cart
        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)

            # Reduce the stock of the product
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Additional logic for saving the selected address to the order
        selected_address = Address.objects.get(pk=selected_address_id)
        order.address = selected_address
        order.save()

        Cart.objects.filter(user=user).delete()        
        
        return redirect('ordersuccess')

    return render(request, 'checkout.html') 

def orderSuccess(request):
    return render(request,'ordersuccess.html')   

def viewOrders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    
    context = {'orders': orders}
    return render(request, 'orders.html', context)

def cancelOrder(request,item_id):
    item = OrderItem.objects.get(pk=item_id)
    item.status ='cancelled'
    item.save()

    return redirect('vieworders')

from django.shortcuts import render
from .models import Product

# def productSearch(request):
#     query = request.GET.get('query')
#     products_list = Product.objects.all()
#     categories = Category.objects.filter(is_listed=True)

#     if query:
#         products_list = products_list.filter(name__icontains=query)

#     context = {
#         'query': query,
#         'products': products_list,
#         'categories': categories,
#     }

#     return render(request, 'searchresult.html', context)
def productSearch(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', 'default')
    categories = Category.objects.filter(is_listed=True)

    # Retrieve products based on search criteria
    products_list = Product.objects.filter(name__icontains=query)

    # Apply sorting criteria
    if sort_by == 'price_low_to_high':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high_to_low':
        products_list = products_list.order_by('-price')
    elif sort_by == 'name_a_to_z':
        products_list = products_list.order_by('name')
    elif sort_by == 'name_z_to_a':
        products_list = products_list.order_by('-name')
    elif sort_by == 'new_arrivals':
        # Your logic for sorting by new arrivals (e.g., based on creation date)
        # Modify as needed
        pass

    context = {
        'query': query,
        'sort_by': sort_by,
        'products': products_list,
        'categories': categories,
    }

    return render(request, 'searchresult.html', context)

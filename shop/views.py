from django.shortcuts import render,redirect
from shop.models import Product,Category,Cart,Order,OrderItem,Wishlist,Coupon
from userpage.models import Address
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import razorpay
from django.http import JsonResponse

#all product view
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

#single product view
def singleProduct(request,item_id):
    item = Product.objects.get(pk=item_id)
    context = {
        'item':item
    }
    return render(request,'singleproduct.html',context)

#wishlist view
def viewWishlist(request):
    if request.user.is_authenticated:    
        user = request.user
        wishlist = Wishlist.objects.filter(user=user)        
        context = {'wishlist':wishlist,}

        return render(request, 'wishlist.html', context)
    return redirect('login')
 


def addtoWishlist(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        user = request.user

        if request.method == 'POST':            
            if Wishlist.objects.filter(user=user, product=product).exists():
                message = 'Product is already in the wishlist.'
            else:
                Wishlist.objects.create(user=user, product=product)
                message = 'Product added to the wishlist.'

            # Return a JSON response with the success message
            return JsonResponse({'message': message})
        else:            
            return JsonResponse({'error': 'Invalid request method.'}, status=400)

    messages.error(request, 'Please log in to add products to your wishlist.')
    return redirect('login')

def deleteWishlist(requst,product_id):
    item = Wishlist.objects.filter(pk=product_id).delete()
    return redirect('wishlist')

#view for adding product to cart 
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
        total_amount = sum(item.calculate_total_amount() for item in cart)

        coupon_code = request.POST.get('coupon')
        applied_coupon = None

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
              
                if coupon.is_valid() and total_amount >= coupon.min_orderamount:
                    total_amount -= coupon.discount_amount
                    applied_coupon = coupon.code
                    request.session['discounted_amount'] = coupon.discount_amount
            except Coupon.DoesNotExist:
                messages.warning(request, 'Invalid coupon code.')

        context = {'cart': cart, 'total_amount': total_amount, 'applied_coupon': applied_coupon}
        return render(request, 'cart.html', context)

    return redirect('login')

#deleting products in cart
def deleteCartItem(reqeust,item_id):
    item = Cart.objects.filter(pk=item_id).delete()
    return redirect('viewcart')

#view checkout pge
def checkOut(request):    
    user = request.user
    cart = Cart.objects.filter(user=user)
    discounted_amount = request.session.get('discounted_amount', 0)
    total_amount = sum(item.product.price * item.quantity for item in cart)
    total_amount -= discounted_amount
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

     
from decimal import Decimal

def processOrder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # Retrieve the discount amount from the session without removing it
    discount_amount = request.session.pop('discounted_amount', 0)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        if not selected_address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')         
        
        # Calculate the total price with the discount
        total_price_with_discount = max(total_amount - discount_amount, Decimal('0'))

        order = Order.objects.create(user=user, total_price=total_price_with_discount, payment_method=payment_method, discount_amount=discount_amount)
        
        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
            
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        selected_address = Address.objects.get(pk=selected_address_id)
        order.address = selected_address
        order.save()

        Cart.objects.filter(user=user).delete()        
        
        return redirect('ordersuccess')

    return render(request, 'checkout.html')


def razorpayOrder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    discount_amount = request.session.pop('discounted_amount', 0)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')
        client = razorpay.Client(auth=("rzp_test_wtY6GWGahBxiu9", "DYOIyhDEEQYis7V5nVo2IeB7"))
        data = { "amount": total_amount*100, "currency": "INR", "receipt": '1' }
        payment = client.order.create(data=data)

        if not selected_address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')
        
        total_price_with_discount = max(total_amount - discount_amount, Decimal('0'))

        order = Order.objects.create(user=user, total_price=total_price_with_discount, payment_method=payment_method, discount_amount=discount_amount)
        
       
        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
          
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
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
    orders = Order.objects.filter(user=user).order_by('-id')
    
    context = {'orders': orders}
    return render(request, 'orders.html', context)

def cancelOrder(request,item_id):
    item = OrderItem.objects.get(pk=item_id)
    item.status ='cancelled'
    item.save()

    return redirect('vieworders')

def requestReturn(request,item_id):
    item = OrderItem.objects.get(pk=item_id)
    item.status = 'return_requested'
    return redirect('vieworders')


def productSearch(request):
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', 'default')
    categories = Category.objects.filter(is_listed=True)

    products_list = Product.objects.filter(name__icontains=query)
    
    if sort_by == 'price_low_to_high':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_high_to_low':
        products_list = products_list.order_by('-price')
    elif sort_by == 'name_a_to_z':
        products_list = products_list.order_by('name')
    elif sort_by == 'name_z_to_a':
        products_list = products_list.order_by('-name')
    elif sort_by == 'new_arrivals':
        products_list = products_list.order_by('-id')
        pass

    context = {
        'query': query,
        'sort_by': sort_by,
        'products': products_list,
        'categories': categories,
    }

    return render(request, 'searchresult.html', context)

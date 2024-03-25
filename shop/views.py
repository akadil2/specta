from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Product,Category,Cart,Order,OrderItem,Wishlist,Coupon
from userpage.models import Address,Wallet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
import razorpay
from django.http import JsonResponse,HttpResponse
from decimal import Decimal
from django.views.decorators.cache import never_cache
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph,Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.template.defaultfilters import floatformat
from reportlab.lib.units import inch
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,F



#all product view
def allProducts(request):
    prod_list = Product.objects.all().order_by('-id')
    paginator = Paginator(prod_list, 9) 

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

            return JsonResponse({'message': message})
        else:            
            return JsonResponse({'error': 'Invalid request method.'}, status=400)

    messages.error(request, 'Please log in to add products to your wishlist.')
    return redirect('login')

def deleteWishlist(requst,product_id):
    item = Wishlist.objects.filter(pk=product_id).delete()
    return redirect('wishlist')
#wishlsit view ends here.

#cart relaated views 
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
            messages.info(request,'Product already in Cart')
    

        else:            
            Cart.objects.create(user=user, product=product, quantity=quantity)
        
        if 'wishlist' in request.headers.get('Referer', ''):
                wishlist_item = Wishlist.objects.filter(product=product, user=user).first()
                if wishlist_item:
                    # Delete the product from the wishlist
                    wishlist_item.delete()

        return redirect('viewcart')

    return redirect('login')


@csrf_exempt
def updateCart(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        new_quantity = int(request.POST.get('new_quantity'))

        try:
            cart_item = Cart.objects.get(pk=cart_item_id)
            cart_item.quantity = new_quantity
            cart_item.save()

            user = request.user
            cart = Cart.objects.filter(user=user)
            
            total_amount = cart.aggregate(total_amount=Sum(F('product__price') * F('quantity')))['total_amount']


            return JsonResponse({'success': True, 'total_amount': total_amount})
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item does not exist'})

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
        discounted_amount = request.session.get('discounted_amount',0)
        context = {'cart': cart, 'total_amount': total_amount, 'applied_coupon': applied_coupon, 'discounted_amount':discounted_amount}
        return render(request, 'cart.html', context)

    return redirect('login')

def deleteCartItem(request,item_id):
    item = Cart.objects.filter(pk=item_id).delete()
    if 'discounted_amount' in request.session:
     del request.session['discounted_amount']
    return redirect('viewcart')

def removeCoupon(request):
    if 'discounted_amount' in request.session:
     del request.session['discounted_amount']
    return redirect('viewcart')
#cart related views ends here.


#views for checkout products from carts
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

     

@never_cache
def processOrder(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    discount_amount = request.session.pop('discounted_amount', 0)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        if not selected_address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')         
        
        total_price_with_discount = max(total_amount - discount_amount, Decimal('0'))

        if 'pay_with_wallet' in request.POST:  
            wallet = Wallet.objects.get(user=user) 

            if wallet.balance >= total_price_with_discount:
                wallet.balance -= Decimal(total_price_with_discount)
                wallet.save()
                payment_method = 'WALLET'
            else:
                messages.error(request, "Insufficient balance in wallet.")
                return redirect('checkout')
        
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
#checkout views ends here.

    
def orderSuccess(request):
    return render(request,'ordersuccess.html')   

#user side order views
def viewOrders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')
    
    context = {'orders': orders}
    return render(request, 'orders.html', context)

def orderDetails(request,order_id):
    user = request.user
    orders = Order.objects.filter(pk=order_id)

    context = {'user':user, 'orders':orders}
    return render(request,'orderdetails.html',context)



def invoicePdf(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)

    # Create a buffer for the PDF content
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # Populate PDF content
    content = []

    # Shop Details
    content.append(Paragraph("<h1>Invoice</h1>", normal_style))
    content.append(Paragraph("<strong>Specta</strong>", normal_style))
    content.append(Paragraph("12b, Calicut", normal_style))
    content.append(Paragraph("info@specta.com", normal_style))
    content.append(Paragraph("<br/><br/>", normal_style))  # Add space between sections

    # User Details
    content.append(Paragraph("<h2>Customer Details:</h2>", normal_style))
    if order.address:
        content.append(Paragraph(f"<strong>Customer Name:</strong> {order.address.name}", normal_style))
        content.append(Paragraph(f"<strong>Address:</strong> {order.address.house_name}, {order.address.city}, {order.address.pin_code}", normal_style))
        content.append(Paragraph(f"<strong>Phone:</strong> {order.address.phone}", normal_style))
    else:
        content.append(Paragraph("<strong>No address available for this order</strong>", normal_style))
    content.append(Paragraph("<br/><br/>", normal_style))  # Add space between sections

    # Invoice Details Table
    table_data = [
        ["Date", "Order ID", "Product Name", "Quantity", "Price", "Discount", "Total"]
    ]

    for order_item in order.orderitem_set.all():  # Access through the intermediate model
        product_name = order_item.product.name
        product_price = order_item.product.price
        quantity = order_item.quantity
        total_amount = product_price * quantity
        
        # Add item details to table data
        table_data.append([
            order.created_at.strftime('%Y-%m-%d'),
            order.id,
            product_name,
            quantity,
            f"{floatformat(product_price, -2)}",
            f"{floatformat(order.discount_amount, -2)}",
            f"{floatformat(total_amount, -2)}"
        ])

    total_price_row = ["", "", "", "", "", "Total Price", f"Rs.{order.total_price}"]
    table_data.append(total_price_row)

    table_style = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, 'BLACK')
    ]

    # Create invoice details table
    invoice_table = Table(table_data)
    invoice_table.setStyle(TableStyle(table_style))

    # Add invoice details table to content
    content.append(invoice_table)

    # Build PDF document
    doc.build(content)

    # Get the PDF content from the buffer
    pdf_data = buffer.getvalue()
    buffer.close()

    # Create HTTP response with PDF content
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    return response

def cancelOrder(request,item_id):
    item = OrderItem.objects.get(pk=item_id)
    if item.status != 'cancelled':  
        item.status = 'cancelled'
        item.save()

        if item.order.payment_method!='COD':
            user = item.order.user
            cancelled_amount = Decimal(item.calculate_amount())

            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.balance += cancelled_amount
            wallet.save()

            messages.success(request, f'Amount of {cancelled_amount} added to your wallet.')

    return redirect('vieworders')
   

def requestReturn(request,item_id):
    item = OrderItem.objects.get(pk=item_id)
    if item.status == OrderItem.DELIVERED:
        item.status = OrderItem.RETURN_REQUESTED
        item.save()
    
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
#userside order views ends here.


def userWallet(request):
    if request.user.is_authenticated:
        # Retrieve the wallet balance for the current user
        wallet = Wallet.objects.filter(user=request.user).first()

        # Pass the wallet balance to the template context
        context = {
            'wallet_balance': wallet.balance if wallet else 0.0,
        }
    
        

    return render(request,'wallet.html',context)

def aboutPage(request):
    return render(request,'about.html')
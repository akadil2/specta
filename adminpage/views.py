from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from userpage.models import Customer,Wallet
from shop.models import Category,Product,Order,OrderItem,Coupon
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas


 
# Create your views here.
    
def adminHome(request, period='month'):
    if request.user.is_authenticated and request.user.is_superuser:
        today = timezone.now()
        start_date = today - timezone.timedelta(days=30)
        
        orders = Order.objects.filter(created_at__gte=start_date)

        total_sales_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_discount_amount = orders.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
        total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

        context = {
            'total_sales_amount': total_sales_amount,
            'total_discount_amount': total_discount_amount,
            'total_sales_count': total_sales_count,
        }

        return render(request, 'admhome.html', context)
    return redirect('login')

def salesReport(request, period='day'):
    if request.user.is_authenticated and request.user.is_superuser:
        today = timezone.now()
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        period = request.GET.get('period', 'month')

        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            if period == 'day':
                start_date = today - timezone.timedelta(days=1)
            elif period == 'week':
                start_date = today - timezone.timedelta(weeks=1)
            elif period == 'month':
                start_date = today - timezone.timedelta(days=30)
            elif period == 'year':
                start_date = today - timezone.timedelta(days=365)
            else:
                return render(request, 'invalid_period.html')

            end_date = today

        orders = Order.objects.filter(created_at__range=[start_date, end_date])

        total_sales_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_discount_amount = orders.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
        total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

        context = {
            'total_sales_amount': total_sales_amount,
            'total_discount_amount': total_discount_amount,
            'total_sales_count': total_sales_count,
            'start_date': start_date,
            'end_date': end_date,
            'period': period,
        }

        return render(request, 'salesreport.html', context)
    return redirect('login')

def generatePdf(request):
    today = timezone.now()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    period = request.GET.get('period', 'month')

    if start_date_str and end_date_str:
        # Custom date range provided
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        # Use predefined period
        if period == 'day':
            start_date = today - timezone.timedelta(days=1)
        elif period == 'week':
            start_date = today - timezone.timedelta(weeks=1)
        elif period == 'month':
            start_date = today - timezone.timedelta(days=30)
        elif period == 'year':
            start_date = today - timezone.timedelta(days=365)
        else:
            return render(request, 'invalid_period.html')

        end_date = today
    
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    
    total_sales_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_discount_amount = orders.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0
    total_sales_count = orders.aggregate(Count('id'))['id__count'] or 0

    context = {
        'total_sales_amount': total_sales_amount,
        'total_discount_amount': total_discount_amount,
        'total_sales_count': total_sales_count,
        'start_date': start_date,
        'end_date': end_date,
        'period': period,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    
    p = canvas.Canvas(response)
    
    # Add information to the PDF
    p.drawString(100, 800, f"Total Sales Count: {total_sales_count}")
    p.drawString(100, 780, f"Total Sales Amount: {total_sales_amount}")
    p.drawString(100, 760, f"Total Discount Amount: {total_discount_amount}")
    p.drawString(100, 740, f"Period: {period.capitalize()}")

    # Save the PDF
    p.showPage()
    p.save()

    return response


def userManage(request):
        if request.user.is_authenticated and request.user.is_superuser:
            cust = Customer.objects.filter(is_superuser=False, is_admin=False)
        
            context = {
            'cust':cust,
            }
            return render (request, 'usermanage.html', context)
        return redirect('login')


def userStatus(request,user_id):
    if request.user.is_authenticated and request.user.is_superuser:
        user = Customer.objects.get(pk=user_id)
        user.is_blocked = not user.is_blocked
        user.save()
        return redirect('usermanage')
    return redirect('login')

def productManage(request):
        if request.user.is_authenticated and request.user.is_superuser:
            prod = Product.objects.all().order_by('-id')
        
            context = {
            'prod':prod,
            }
            return render(request, 'productmanage.html', context)
        return redirect('login')

@login_required(login_url='/login/')
def addProduct(request):
        categories = Category.objects.all()
        if request.method == 'POST':
          prod = request.POST.get('name')
          desc = request.POST.get('description')
          price = request.POST.get('price')
          stock = request.POST.get('stock')
          category_id = request.POST.get('category')
          image = request.FILES.get('image')
          image1 = request.FILES.get('image1')
          image2 = request.FILES.get('image2')
          cat = Category.objects.get(id=category_id)
          if len(prod.replace(" ", "")) < 2:
            messages.error(request, "Enter a valid Name.")
            return render(request,'addproduct.html',{'categories': categories})
          
          prod = Product.objects.create(name=prod,description=desc,price=price,stock=stock,category=cat,image=image,image1=image1,image2=image2)
          prod.save()
          return redirect('productmanage')
        return render(request,'addproduct.html',{'categories': categories}) 

def productStatus(request,item_id):
    if request.user.is_authenticated and request.user.is_superuser:
        item = Product.objects.get(pk=item_id)
        item.is_listed = not item.is_listed
        item.save()
        return redirect('productmanage')
    return redirect('login')

@login_required(login_url='/login/')
def editProduct(request,item_id):
        categories = Category.objects.all()
        
        item = Product.objects.get(id = item_id)
        if request.method == 'POST':
                prod1 = Product.objects.get(id=item_id)

                prod = request.POST.get("name")
                desc = request.POST.get("description")
                price = request.POST.get('price')
                stock = request.POST.get('stock')
                category_id = request.POST.get('category')
                image = request.FILES.get('image')
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')

                if not image:
                        image = prod1.image
                if not image1:
                        image1 = prod1.image1
                if not image2:
                        image2 = prod1.image2

                if category_id is None:
                        category_id = prod1.category.id
                cat = Category.objects.get(id=category_id)

                prod1.name = prod
                prod1.description = desc
                prod1.price = price
                prod1.stock = stock
                prod1.category = cat
                prod1.image = image
                prod1.image1 = image1
                prod1.image2 = image2

                prod1.save()

                return redirect("productmanage")

        return render(request, 'editproduct.html', {'categories': categories, 'item': item})


def categoryManage(request):
        if request.user.is_authenticated and request.user.is_superuser:        
            cat = Category.objects.all().order_by('-id')
        
            context = {
            'cat':cat,
            }
            return render(request, 'categorymanage.html', context)
        return redirect('login')

@login_required(login_url='/login/')
def addCategory(request):
        if request.method == 'POST':
          cat = request.POST.get('category')
          desc = request.POST.get('description')
          existing_category = Category.objects.filter(name__iexact=cat.replace(" ", ""))
          if existing_category.exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('addcategory')
          categ = Category.objects.create(name=cat,description=desc)
          categ.save()
          return redirect('categorymanage')
        return render(request,'addcategory.html') 

def categoryStatus(request,item_id):
    if request.user.is_authenticated and request.user.is_superuser:
        item = Category.objects.get(pk=item_id)
        item.is_listed = not item.is_listed
        item.save()
        return redirect('categorymanage')
    return redirect('login')

@login_required(login_url='/login/')
def editCategory(request, item_id):
    category = get_object_or_404(Category, pk=item_id)

    if request.method == 'POST':
        cat = request.POST.get('name')
        desc = request.POST.get('description')
        if len(cat.replace(" ", "")) < 2:
            messages.error(request, "Category name should contain at least two letters excluding spaces.")
            return render(request, 'editcategory.html', {'item': category})
        category.name = cat
        category.description = desc
        category.save()
        return redirect('categorymanage')

    return render(request, 'editcategory.html', {'item': category})


def deleteCategory(request,item_id):
        if request.user.is_authenticated and request.user.is_superuser:
            item = Category.objects.filter(pk=item_id).delete()
            return redirect('categorymanage')
        return redirect('login')
       

def orderManage(request):
        if request.user.is_authenticated and request.user.is_superuser:
            orders = OrderItem.objects.all().order_by('-id')
            context = {
                'orders':orders,              
            }
            return render(request, 'manageorders.html',context)
        return redirect('login')

@login_required(login_url='/login/')

def orderStatus(request, order_id):
    order_item = get_object_or_404(OrderItem, pk=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status == 'cancelled' and order_item.status != 'cancelled':
            order_item.status = new_status
            order_item.save()

            # Credit the cancelled amount to the user's wallet
            if order_item.order.payment_method != 'COD':
                user = order_item.order.user
                cancelled_amount = Decimal(order_item.calculate_amount())

                wallet, created = Wallet.objects.get_or_create(user=user)
                wallet.balance += cancelled_amount
                wallet.save()

                messages.success(request, f'Amount of {cancelled_amount} added to user wallet.')
        elif new_status == 'shipped' and order_item.status != 'shipped':
            order_item.status = new_status
            order_item.save()

        elif new_status == 'delivered' and order_item.status != 'delivered':
            order_item.status = new_status
            order_item.save()
            
    return redirect('ordermanage')

def acceptReturn(request,order_id):
    order_item = get_object_or_404(OrderItem, pk=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status == 'returned':           
            user = order_item.order.user

            returned_amount = Decimal(order_item.calculate_amount())
           
            wallet, created = Wallet.objects.get_or_create(user=user)
           
            wallet.balance += returned_amount
            wallet.save()

            order_item.status = new_status
            order_item.save()

            messages.success(request, f'Amount of {returned_amount} added to your wallet.')

    return redirect('ordermanage')
      

def couponManage(request):
      if request.user.is_authenticated and request.user.is_superuser:
        coupon = Coupon.objects.all().order_by('-id')
        
        context = {
            'coupon':coupon,
            }
        return render(request, 'couponmanage.html', context)
      return redirect('login')

def addCoupon(request):
      if request.method == 'POST':
          code = request.POST.get('code')
          discount = request.POST.get('discount_amount')
          minorder = request.POST.get('minorder_amount')          
          valid_from = request.POST.get('valid_from')
          valid_to = request.POST.get('valid_to')

          validfrom = datetime.strptime(valid_from, '%Y-%m-%d').date()
          validto = datetime.strptime(valid_to, '%Y-%m-%d').date()

          coupon = Coupon.objects.create(code=code,discount_amount=discount,min_orderamount=minorder,valid_from=validfrom,valid_to=validto)
          coupon.save()
          return redirect('couponmanage')
      return render(request,'addcoupon.html')

def admLogout(request):
       if request.user.is_authenticated:
              logout(request)
       return render(request,'index.html')



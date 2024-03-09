from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from userpage.models import Customer
from shop.models import Category,Product,Order,OrderItem,Coupon
from django.contrib.auth.decorators import login_required
from datetime import datetime
# Create your views here.

    
def adminHome(request):
#        if request.user.is_authenticated:
        return render(request, 'admhome.html')
#        return redirect('home')

def admLogout(request):
       if request.user.is_authenticated:
              logout(request)
       return render(request,'index.html')
       

# @login_required
def userManage(request):
        cust = Customer.objects.filter(is_superuser=False, is_admin=False)
     
        context = {
        'cust':cust,
        }
        return render (request, 'usermanage.html', context)

# @login_required
def userStatus(request,user_id):
    user = Customer.objects.get(pk=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect('usermanage')

@login_required
def productManage(request):
        prod = Product.objects.all().order_by('-id')
     
        context = {
        'prod':prod,
        }
        return render(request, 'productmanage.html', context)

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
          
          prod = Product.objects.create(name=prod,description=desc,price=price,stock=stock,category=cat,image=image,image1=image1,image2=image2)
          prod.save()
          return redirect('productmanage')
        return render(request,'addproduct.html',{'categories': categories}) 

@login_required
def productStatus(request,item_id):
    item = Product.objects.get(pk=item_id)
    item.is_listed = not item.is_listed
    item.save()
    return redirect('productmanage')


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

                # Keep the current image if no new image is provided in the form
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



# def deleteProduct(request,item_id):
#        item = Product.objects.filter(pk=item_id).delete()
#        return redirect('productmanage')

# @login_required
def categoryManage(request):
        cat = Category.objects.all().order_by('-id')
     
        context = {
        'cat':cat,
        }
        return render(request, 'categorymanage.html', context)

def addCategory(request):
        if request.method == 'POST':
          cat = request.POST.get('category')
          desc = request.POST.get('description')
          categ = Category.objects.create(name=cat,description=desc)
          categ.save()
          return redirect('categorymanage')
        return render(request,'addcategory.html') 

def categoryStatus(request,item_id):
    item = Category.objects.get(pk=item_id)
    item.is_listed = not item.is_listed
    item.save()
    return redirect('categorymanage')

def editCategory(request, item_id):
    category = get_object_or_404(Category, pk=item_id)

    if request.method == 'POST':
        cat = request.POST.get('name')
        desc = request.POST.get('description')
        category.name = cat
        category.description = desc
        category.save()
        return redirect('categorymanage')

    return render(request, 'editcategory.html', {'item': category})

def deleteCategory(request,item_id):
       item = Category.objects.filter(pk=item_id).delete()
       return redirect('categorymanage')

def orderManage(request):
        orders = OrderItem.objects.all().order_by('-id')
        context = {
              'orders':orders,              
        }
        return render(request, 'manageorders.html',context)

def orderStatus(request,item_id):
      order_item = get_object_or_404(OrderItem, pk=item_id)

      if request.method == 'POST':
        order_item.status = request.POST.get('status')
        order_item.save()

      return redirect('ordermanage')

def couponManage(request):
      coupon = Coupon.objects.all().order_by('-id')
     
      context = {
        'coupon':coupon,
        }
      return render(request, 'couponmanage.html', context)

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
      
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout,get_user_model,update_session_auth_hash
from django.contrib.auth.models import User
from .models import Customer,Address
from django.core.mail import send_mail
from django.conf import settings
import random
from smtplib import SMTPException
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache
import re





# Create your views here.

def homePage(request):
    # if request.user.is_authenticated:
        return render(request,'index.html')
    # return redirect('home')
    

def signin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:            
            return redirect('adminhome')
        else:            
            return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        user = authenticate(request, username=username, password=password)
        print(user)
        

        if user is not None and isinstance(user, Customer):
            if user.is_superuser:                
                login(request, user)
                return redirect('adminhome')
            elif not user.is_blocked:                
                login(request, user)
                return redirect('home')
            else:
                if user.is_blocked:
                    messages.error(request, 'Your account is blocked. Please contact support.')
                else:
                    messages.error(request, 'Invalid Credentials!!')

    return render(request, 'login.html')

    

# views for new user signup #

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def signUp(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'signup.html')

        if not uname.isalnum():
            messages.error(request, 'Username should only contain letters and numbers')
            return render(request, 'signup.html')

        if not password1.isalnum():
            messages.error(request, 'Password should be alphanumeric')
            return render(request, 'signup.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email address')
            return render(request, 'signup.html')
        
        if not re.match(r'^(?!0+$)\d{10}$', phone):
            messages.error(request, 'Invalid phone number')
            return render(request, 'signup.html')

        if get_user_model().objects.filter(username=uname).exists():
            messages.error(request, 'Username is already taken')
            return render(request, 'signup.html')
        
        if get_user_model().objects.filter(email=email).exists():
            messages.error(request, 'email alredy registered use another')
            return render(request, 'signup.html')

        user = get_user_model()(
            first_name=name,
            username=uname,
            email=email,
            phone_number=phone,
        )
        user.set_password(password1)        
        
        otp = generate_otp()
        user.otp = otp
        user.save()

        # Send OTP via email
        subject = 'Verify your email for  Specta registration'
        message = f'Your verification OTP is: {otp}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        try:
            send_mail(subject, message, from_email, [to_email])
            messages.success(request, 'An OTP has been sent to your email. Please check and enter it.')
            return redirect('verifyemail', user_id=user.id)
        except Exception as e:            
            user.delete()
            messages.error(request, f'Error sending OTP email: {str(e)}')
            return redirect('signup')

    return render(request, 'signup.html')
#------------------#

def verifyEmail(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == user.otp:        
            user.is_verified = True
            user.save()
            messages.success(request, 'Email verification successful. You can now log in.')
            return redirect('login')  
        else:            
            user.delete()  
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verifyemail.html', {'user': user})


def logOut(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

def userProfile(request):    
    user= request.user
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        uname = request.POST.get('uname')
        phone = request.POST.get('phone')
        user.first_name = fname
        user.last_name = lname
        user.username = uname
        user.phone_number = phone
        user.save()
        return redirect('userprofile')

    return render(request,'userprofile.html', {'user':user})

def editAddress(request, ad_id):    
    address = Address.objects.get(pk=ad_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        hname = request.POST.get('house_name')
        phone = request.POST.get('phone')
        post = request.POST.get('post')
        city = request.POST.get('city')
        pincode = request.POST.get('pin_code')
        state = request.POST.get('state')

    
        address.name = name
        address.house_name = hname
        address.phone = phone
        address.post = post
        address.city = city
        address.pin_code = pincode
        address.state = state
        address.save()

        return redirect('address')

    return render(request, 'address.html', {'address': address})

def editProfile(request):
    return render(request,'editprofile.html')

def userAddress(request):
    addres = Address.objects.filter(user=request.user)
    return render(request, 'address.html', {'addres': addres})

def newAddress(request):
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
        return redirect('address')
            

    return render(request,'newaddress.html')

from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash

def changePassword(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentpassword')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user = request.user

        # Authenticate the user with their current password
        user_authenticated = authenticate(username=user.username, password=current_password)

        if user_authenticated is not None:
            # Current password is correct, proceed with password change
            if password1 == password2:
                user.set_password(password1)
                user.save()

                # Update the session to avoid logout after changing the password
                update_session_auth_hash(request, user)

                messages.success(request, 'Password changed successfully.')
                return redirect('userprofile')
            else:
                messages.error(request, 'New passwords do not match.')
        else:
            messages.error(request, 'Current password is incorrect.')

    return render(request, 'changepassword.html')

# def forgotPassword(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
        

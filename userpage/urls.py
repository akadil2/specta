from django.urls import path
from . import views


urlpatterns = [

    path('', views.homePage, name='home'),
    path('login/', views.signin, name='login'),
    path('signup/',views.signUp, name='signup'),
    path('verifyemail/<int:user_id>',views.verifyEmail, name='verifyemail'),
    path('logout/', views.logOut, name='logout'),
    path('userprofile/', views.userProfile, name='userprofile'),
    path('editprofile/', views.editProfile, name='editprofile'),
    path('address/',views.userAddress, name='address'),
    path('newaddress/',views.newAddress, name='newaddress'),
    path('editaddress/<int:ad_id>',views.editAddress, name='editaddress'),
    path('deleteaddress/<int:ad_id>',views.deleteAddress, name='deleteaddress'),
    path('changepassword/',views.changePassword, name='changepassword')

    
]    
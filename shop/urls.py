from django.urls import path
from . import views


urlpatterns = [

    path('allproducts/',views.allProducts, name='allproducts'),
    path('singleproduct/<int:item_id>',views.singleProduct,name='singleproduct'),
    path('wishlist/', views.viewWishlist, name='wishlist'),
    path('addtowishlist/<int:product_id>/', views.addtoWishlist, name='addtowishlist'),
    path('deletewishlist/<int:product_id>/', views.deleteWishlist, name='deletewishlist'),
    path('addtocart/<int:product_id>/', views.addtoCart, name='addtocart'),
    path('viewcart/', views.viewCart, name='viewcart'),
    path('updatecart/', views.updateCart, name='updatecart'),
    path('deletecartitem/<int:item_id>/', views.deleteCartItem, name='deletecartitem'),
    path('removecoupon/', views.removeCoupon, name='removecoupon'),
    path('checkout/', views.checkOut, name='checkout'),
    path('addnewaddress/',views.addnewAddress, name='addnewaddress'),
    path('processorder/', views.processOrder, name='processorder'),
    path('ordersuccess/', views.orderSuccess, name='ordersuccess'),
    path('vieworders/', views.viewOrders, name='vieworders'),
    path('orderdetails/<int:order_id>/', views.orderDetails, name='orderdetails'),
    path('invoicepdf/<int:order_id>/', views.invoicePdf, name='invoicepdf'),
    path('cancelorder/<int:item_id>/', views.cancelOrder, name='cancelorder'),
    path('returnorder/<int:item_id>/', views.requestReturn, name='returnorder'),
    path('productsearch/', views.productSearch, name='productsearch'),
    path('userwallet/', views.userWallet, name='userwallet'),
    path('aboutpage/', views.aboutPage, name='aboutpage'),

]
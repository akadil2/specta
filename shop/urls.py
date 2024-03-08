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
    path('deletecartitem/<int:item_id>/', views.deleteCartItem, name='deletecartitem'),
    path('applycoupon/', views.applyCoupon, name='applycoupon'),
    path('checkout/', views.checkOut, name='checkout'),
    path('addnewaddress/',views.addnewAddress, name='addnewaddress'),
    path('processorder/', views.processOrder, name='processorder'),
    path('razorpayorder/',views.razorpayOrder,name='razorpayorder'),
    path('ordersuccess/', views.orderSuccess, name='ordersuccess'),
    path('vieworders/', views.viewOrders, name='vieworders'),
    path('cancelorder/<int:item_id>/', views.cancelOrder, name='cancelorder'),
    path('productsearch/', views.productSearch, name='productsearch'),

]
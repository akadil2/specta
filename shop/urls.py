from django.urls import path
from . import views


urlpatterns = [

    path('allproducts/',views.allProducts, name='allproducts'),
    path('singleproduct/<int:item_id>',views.singleProduct,name='singleproduct'),
    path('addtocart/<int:product_id>/', views.addtoCart, name='addtocart'),
    path('viewcart/', views.viewCart, name='viewcart'),
    path('deletecartitem/<int:item_id>/', views.deleteCartItem, name='deletecartitem'),
    path('checkout/', views.checkOut, name='checkout'),
    path('processorder/', views.processOrder, name='processorder'),
    path('vieworders/', views.viewOrders, name='vieworders'),
    path('cancelorder/<int:item_id>/', views.cancelOrder, name='cancelorder'),
    path('productsearch/', views.productSearch, name='productsearch'),

]
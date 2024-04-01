from django.urls import path
from . import views

urlpatterns = [

    path('adminhome/',views.adminHome,name='adminhome'),
    path('salesreport/',views.salesReport,name='salesreport'),
    path('generatepdf/',views.generatePdf,name='generatepdf'),
    path('usermanage/',views.userManage,name='usermanage'),
    path('userstatus/<int:user_id>',views.userStatus,name='userstatus'),
    path('productmanage/',views.productManage,name='productmanage'),
    path('addproduct/',views.addProduct,name='addproduct'),
    path('productstatus/<int:item_id>',views.productStatus,name='productstatus'),
    path('editproduct/<str:item_id>',views.editProduct,name='editproduct'),
    path('categorymanage/',views.categoryManage,name='categorymanage'),
    path('addcategory/',views.addCategory,name='addcategory'),
    path('categorystatus/<int:item_id>',views.categoryStatus,name='categorystatus'),
    path('editcategory/<int:item_id>', views.editCategory, name='editcategory'),
    path('deletecategory/<int:item_id>',views.deleteCategory,name='deletecategory'),
    path('ordermanage/',views.orderManage,name='ordermanage'),
    path('orderstatus/<int:order_id>/', views.orderStatus, name='orderstatus'),
    path('userorders/<int:order_id>/', views.userOrders, name='userorders'),
    path('acceptreturn/<int:order_id>/', views.acceptReturn, name='acceptreturn'),
    path('couponmanage/',views.couponManage,name='couponmanage'),
    path('couponstatus/<int:coupon_id>',views.couponStatus,name='couponstatus'),
    path('addcoupon/',views.addCoupon, name='addcoupon'),
    path('adminlogout/',views.admLogout, name='adminlogout')
    
    
]   
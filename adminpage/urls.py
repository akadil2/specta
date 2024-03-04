from django.urls import path
from . import views

urlpatterns = [

    path('adminhome/',views.adminHome,name='adminhome'),
    path('usermanage/',views.userManage,name='usermanage'),
    path('userstatus/<int:user_id>',views.userStatus,name='userstatus'),
    path('productmanage/',views.productManage,name='productmanage'),
    path('addproduct/',views.addProduct,name='addproduct'),
    path('productstatus/<int:item_id>',views.productStatus,name='productstatus'),
    # path('deleteproduct/<int:item_id>',views.deleteProduct,name='deleteproduct'),
    path('editproduct/<str:item_id>',views.editProduct,name='editproduct'),
    path('categorymanage/',views.categoryManage,name='categorymanage'),
    path('addcategory/',views.addCategory,name='addcategory'),
    path('categorystatus/<int:item_id>',views.categoryStatus,name='categorystatus'),
    path('editcategory/<int:item_id>', views.editCategory, name='editcategory'),
    path('deletecategory/<int:item_id>',views.deleteCategory,name='deletecategory'),
    path('ordermanage/',views.orderManage,name='ordermanage'),
    path('orderstatus/<int:item_id>/', views.orderStatus, name='orderstatus'),
    path('adminlogout/',views.admLogout, name='adminlogout')
    
    
]   
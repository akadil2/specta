# forms.py
# from django import forms
# from shop.models import Product,Category

# class ProductEditForm(forms.ModelForm):
#     name = forms.CharField(max_length=255)
#     description = forms.CharField(widget=forms.Textarea)
#     price = forms.DecimalField(max_digits=10, decimal_places=2)
#     category = forms.ModelChoiceField(queryset=Category.objects.all())
#     image = forms.ImageField()

    
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'category', 'image']

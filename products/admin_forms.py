from django import forms
from .models import Product, Category, ProductVariant


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Category name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'auto-generated-slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'ingredients', 'usage_info',
                  'category', 'base_price', 'image', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Product name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'auto-generated-slug'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Product description'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Comma-separated ingredients'
            }),
            'usage_info': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'How to use this product'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['weight_label', 'price', 'stock_quantity']
        widgets = {
            'weight_label': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 100g'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': '0'
            }),
        }


ProductVariantFormSet = forms.inlineformset_factory(
    Product, ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True,
)

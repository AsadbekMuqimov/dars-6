from django.shortcuts import render, redirect, get_object_or_404
from Goods import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.db import transaction


@login_required
def mycart(request):
    cart, created = models.Cart.objects.get_or_create(
        author=request.user, 
        is_active=True,
        defaults={'author': request.user}
    )
    context = {'cart': cart}
    return render(request, 'Goods/mycart.html', context)


@login_required
def addProductToCart(request):
    code = request.GET.get('code')
    quantity = request.GET.get('quantity')
    if not code or not quantity:
        return HttpResponseBadRequest("Miqdor kam")
    try:
        quantity = int(quantity)
        product = get_object_or_404(models.Product, generate_code=code)
        cart, _ = models.Cart.objects.get_or_create(author=request.user, is_active=True)
        cart_product, created = models.CartProduct.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_product.quantity += quantity
        else:
            cart_product.quantity = quantity
        cart_product.save()
        return redirect('/')
    except ValueError:
        return HttpResponseBadRequest("Miqdor xatoligi")


@login_required
def create_order(request):
    generate_code = request.GET.get('generate_code')
    phone = request.GET.get('phone')
    address = request.GET.get('address')

    if not generate_code or not phone or not address:
        return HttpResponseBadRequest("Missing required parameters.")

    try:
        cart = models.Cart.objects.get(generate_code=generate_code, author=request.user, is_active=True)
    except models.Cart.DoesNotExist:
        return HttpResponseBadRequest("Cart not found.")

    cart_products = models.CartProduct.objects.filter(cart=cart)
    done_products = []

    with transaction.atomic():
        for cart_product in cart_products:
            if cart_product.quantity <= cart_product.product.quantity:
                cart_product.product.quantity -= cart_product.quantity
                cart_product.product.save()
                done_products.append(cart_product)
            else:
                for product in done_products:
                    product.product.quantity += product.quantity
                    product.product.save()
                return HttpResponseBadRequest("Insufficient quantity in stock.")

        models.Order.objects.create(
            cart=cart,
            full_name=f"{request.user.first_name} {request.user.last_name}",
            email=request.user.email,
            phone=phone,
            address=address,
            status=1
        )

        cart.is_active = False
        cart.save()

    return redirect('/')

def subtract_from_cart(request):
    code = request.GET.get('code')
    try:
        quantity = int(request.GET.get('quantity', 1))
    except ValueError:
        return HttpResponseBadRequest("Invalid quantity value.")
    
    if not code:
        return HttpResponseBadRequest("Missing code in request.")
    
    try:
        product_cart = models.CartProduct.objects.get(
            product__generate_code=code,
            cart__author=request.user,
            cart__is_active=True
        )
        if product_cart.quantity <= quantity:
            product_cart.delete()
        else:
            product_cart.quantity -= quantity
            product_cart.save()
    except models.CartProduct.DoesNotExist:
        return HttpResponseBadRequest("Product not found in cart.")
    
    return redirect('mycart')


def delete_from_cart(request):
    code = request.GET.get('code')
    try:
        product_cart = models.CartProduct.objects.get(product__generate_code=code, cart__user=request.user, cart__is_active=True)
        product_cart.delete()
    except models.CartProduct.DoesNotExist:
        pass
    return redirect('mycart')


    
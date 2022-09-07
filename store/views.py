from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


from django.views.decorators.csrf import csrf_exempt

from .models import *
import datetime
import json

from .cartdata import cookieCart, cartData, guestOrder

# Create your views here.


def store(request):

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/Store.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'store/Cart.html', context)


def checkout(request):

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/Checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)  # extract request data as a dictionary
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt  # marks a view as being exempt from the protection ensured by the middleware
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()

    data = json.loads(request.body)  # parse the data

    if request.user.is_authenticated:

        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    # for all users

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:  # protection against users manipulating our data on the frontend
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(  # create attrib of a model and pass values
            customer=customer,
            order=order,
            address=data['shipping']['address'],  # sent form data
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            # date will be added automatically
        )

    return JsonResponse('Payment done', safe=False)

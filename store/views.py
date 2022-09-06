from django.shortcuts import render
from django.http import HttpResponse, JsonResponse


from django.views.decorators.csrf import csrf_exempt

from .models import *
import datetime
import json

# Create your views here.


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/Store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(  # returns tuple where order is an object, created is a boolean
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])  # returns a python dict
        except:
            # if we don't have cart Cookies yet, create empty value
            cart = {}

        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

        for i in cart:
            try:
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'id': product.id,
                    'product': {'id': product.id, 'name': product.name, 'price': product.price,
                                'imageURL': product.imageURL}, 'quantity': cart[i]['quantity'],
                    'digital': product.digital, 'get_total': total,
                }

                items.append(item)  # append created dict to a list

                if product.digital == False:  # if shipping is needed
                    order['shipping'] = True

            except:
                pass

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'store/Cart.html', context)


def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

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
    else:
        print('User is not logged in')

    return JsonResponse('Payment done', safe=False)

from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.http import HttpResponse
from .models import *
from .form import *
from django.contrib.auth.decorators import login_required
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user, allowed_user, admin_only
from django.contrib.auth.models import Group
# Create your views here.

# Test


@login_required(login_url='login')
def home(req):

    orders = Order.objects.all()
    orders_firts = orders[:5]
    customers = Customer.objects.all()

    total_customer = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivery").count()
    pending = orders.filter(status='Pending').count()

    contex = {"orders": orders,'orders_firts': orders_firts , "customers": customers,
              'total_customer': total_customer, "total_orders": total_orders, 'delivered': delivered, 'pending': pending}

    return render(req, 'accounts/dashboard.html', contex)


@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def user(req):
    orders = req.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()
    context = {'orders': orders, 'delivered': delivered, 'pending': pending, 'total_orders': total_orders}
    print ("ORDERS:", orders)
    return render(req, 'accounts/user.html', context)


@unauthenticated_user
def loginPage(req):

    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(req, username=username, password=password)

        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.info(req, 'Username or password is incorrect')

    context = {}
    return render(req, "accounts/login.html", context)


def logOutUser(req):
    logout(req)
    return redirect('login')


@unauthenticated_user
def registerPage(req):

    form = CreateUserForm()

    if req.method == "POST":
        form = CreateUserForm(req.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')

            messages.success(req, 'Account was created for ' + username)

            return redirect('login')

    context = {"form": form}
    return render(req, "accounts/register.html", context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def products(req):
    products = Product.objects.all()

    return render(req, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customer(req, pk_test):
    customer = Customer.objects.get(id=pk_test)

    orders = customer.order_set.all()

    order_count = orders.count()

    myFilter = OrderFilter(req.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders,
               'orders_count': order_count, 'myFilter': myFilter}

    return render(req, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def createOrder(req, pk):
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderFrom(initial={"customer": customer})
    if req.method == 'POST':
        # print ('Printing post:', req.POST)
        # form = OrderFrom(req.POST)
        formset = OrderFormSet(req.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset}

    return render(req, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def updateOrder(req, pk):
    order = Order.objects.get(id=pk)
    form = OrderFrom(instance=order)

    if req.method == 'POST':
        # print ('Printing post:', req.POST)
        form = OrderFrom(req.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {'form': form}
    return render(req, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_user(allowed_roles=['customer'])
def accountSettings(req):
    customer = req.user.customer
    form = CustomerForm(instance=customer)

    if req.method == 'POST':
        form = CustomerForm(req.POST, req.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(req, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def deleteOrder(req, pk):
    order = Order.objects.get(id=pk)
    if req.method == "POST":
        order.delete()
        return redirect('/')

    context = {'item': order}
    return render(req, 'accounts/delete.html', context)




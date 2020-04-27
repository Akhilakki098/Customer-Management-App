from django.shortcuts import render,redirect
from django.http import *
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate,login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.

from .models import *
from .forms import *
from .filters import *
from .decorators import *



@unauthenticated_user
def registerPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for ' + username)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'crmapp/register.html', context)

    
    

@unauthenticated_user
def loginPage(request):
        
    if request.method=='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request,username = username , password=password)


            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request,'Username or Password is incorrect')
                
            
        
    context = {}
    return render(request,'crmapp/login.html',context)


def logoutUser(request):
        logout(request)
        return redirect('login')


@login_required(login_url='login')#(decorators used in django)
@admin_only
def home(request):
    orders = Order.objects.all()#django database query)#will display list of all the customers
    customers = Customer.objects.all()


    total_customers = customers.count()#database query to count total no. of customers
    total_orders = orders.count()#database query to count total no. of orders
    delivered = orders.filter(status='Delivered').count()
    
    pending = orders.filter(status='Pending').count()

    


    context = {'orders':orders,'customers':customers,'total_orders':total_orders,
               'delivered':delivered,'pending':pending}
    
    return render(request,'crmapp/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customers'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()#database query to count total no. of orders
    delivered = orders.filter(status='Delivered').count()
    
    pending = orders.filter(status='Pending').count()
    print('ORDERS:',orders)
    context = {'orders':orders,'total_orders':total_orders,
               'delivered':delivered,'pending':pending}
    return render(request,'crmapp/user.html',context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['customers'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()


	context = {'form':form}
	return render(request, 'crmapp/account_settings.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products=Product.objects.all()
    return render(request,'crmapp/products.html',{'products':products})



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):

    customer = Customer.objects.get(id=pk_test)
    
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter = OrderFilter(request.GET,queryset= orders)
    orders = myFilter.qs
    
    context = {'customer':customer,'orders':orders,'order_count':order_count,'myFilter': myFilter}
    return render(request,'crmapp/customers.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createorder(request,pk):
    OrderFormSet = inlineformset_factory(Customer,Order,fields=('product','status'),extra=5)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
   #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST':
        #print('printing POST:',request.POST)
        #form=OrderForm(request.POST)
        formset = OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
        
    context={'formset':formset,'customer':customer}
    return render(request,'crmapp/order_form.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        #print('printing POST:',request.POST)
        form=OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}
    return render(request,'crmapp/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {'item':order}
    return render(request,'crmapp/delete.html',context)
    

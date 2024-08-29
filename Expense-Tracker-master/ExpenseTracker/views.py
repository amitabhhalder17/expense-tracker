from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ExpenseTracker.models import Exp
from ExpenseTracker.forms import stform
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

def login(request):
    if request.method == "POST":
        fm = AuthenticationForm(request=request, data=request.POST)
        if fm.is_valid():
            uname = fm.cleaned_data['username']
            upass = fm.cleaned_data['password']
            user = authenticate(username=uname, password=upass)
            if user is not None:
                auth_login(request, user)
                return redirect('display', user_id=user.id)
            else:
                messages.error(request, 'Invalid username or password')
    else:
        fm = AuthenticationForm()
    return render(request, 'login.html', {'form': fm})

def register(request):
    if request.method == "POST":
        fm = UserCreationForm(request.POST)
        if fm.is_valid():
            fm.save()
            username = fm.cleaned_data.get('username')
            password = fm.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Registration successful')
                return redirect('display', user_id=user.id)
    else:
        fm = UserCreationForm()
    return render(request, 'register.html', {'form': fm})

@login_required
def insert(request, user_id):
    display_course = User.objects.get(id=user_id)
    if request.method == "GET":
        return render(request, 'create.html', {'display': display_course})
    elif request.method == "POST":
        try:
            des = request.POST['des']
            amt = request.POST['amt']
            date = request.POST['date']
            pay = request.POST['pay']
            Exp(des=des, amt=amt, date=date, pay=pay, owner_id=user_id).save()
            messages.success(request, 'Record saved successfully')
            return render(request, 'create.html', {'display': display_course})
        except Exception as e:
            messages.error(request, 'Failed to save record')
    return render(request, 'create.html', {'display': display_course})

@login_required
def create(request):
    return render(request, 'create.html')

@login_required
def show_expense(request, user_id):
    point = User.objects.get(id=user_id)
    results = Exp.objects.filter(owner=point)
    return render(request, 'index.html', {"Exp": results})

@login_required
def dash(request, user_id):
    point = User.objects.get(id=user_id)
    results = Exp.objects.filter(owner=point)
    return render(request, 'dashboard1.html', {"Exp": results})

@login_required
def edit(request, id):
    getexpense = Exp.objects.get(id=id)
    return render(request, 'edit.html', {"Exp": getexpense})

@login_required
def stupdate(request, id):
    stupdate = Exp.objects.get(id=id)
    form = stform(request.POST, instance=stupdate)
    if form.is_valid():
        form.save()
        messages.success(request, 'Expense updated successfully')
        return redirect('edit', id=id)
    return render(request, 'edit.html', {"Exp": stupdate})

@login_required
def stdel(request, id):
    delstudent = Exp.objects.get(id=id)
    delstudent.delete()
    owner = User.objects.get(id=request.user.id)
    results = Exp.objects.filter(owner=owner)
    return render(request, 'dashboard1.html', {"Exp": results})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def piechart(request, user_id):
    labels = []
    data = []
    point = User.objects.get(id=user_id)
    queryset = Exp.objects.filter(owner=point)
    for city in queryset:
        labels.append(city.des)
        data.append(city.amt)
    explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    fig1, ax1 = plt.subplots()
    ax1.pie(data, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig('static/css/images.png', dpi=100)
    return render(request, 'pie.html')

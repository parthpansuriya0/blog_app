from django.shortcuts import render,redirect
from django.http import request
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator

def home(request):
    blogs = Blog.objects.all().order_by('-post_date')
    context = {'header' :'Blog App','blogs':blogs}
    return render(request,"home.html", context)

def blogs(request):
    blogs = Blog.objects.all().order_by('-post_date')
    paginator = Paginator(blogs, 2)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)

    context = {'header' :'Blogs','blogs':blogs}
    return render(request,"blogs.html", context)

def blog_detail(request,id):
    blog = Blog.objects.filter(id=id).first()
    context = {'header' :'Blog Detail','blog':blog}
    return render(request,"blog_detail.html", context)

def bloggers(request):
    bloggers = CustomUser.objects.all()
    context = {'header' :'Bloggers','bloggers':bloggers}
    return render(request,"bloggers.html", context)

def blogger_detail(request,id):
    blogger = CustomUser.objects.filter(id=id).first()
    context = {'header' :'Blogger Detail','blogger':blogger}
    return render(request,"blogger_detail.html", context)

def register_page(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        gender = request.POST['gender']
        age = request.POST['age']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.warning(request, 'Passwords don\'t match.')
            return render(request, 'register_page.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists.')
            return render(request, 'register_page.html')

        user = CustomUser(username=username, email=email, gender=gender, age=age, password=make_password(password))
        user.save()

        login(request, user)
        return redirect('login_page')

    context = {'header' :'Register'}
    return render(request,"register_page.html", context)

def login_page(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.warning(request, 'Invalid email or password.')
            return render(request, 'login_page.html')

    context = {'header' :'Login'}
    return render(request,"login_page.html", context)

def logout_page(request):
    logout(request)
    return redirect('login_page')

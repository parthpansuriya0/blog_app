from django.shortcuts import render,redirect
from django.http import request
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from BlogApp.serializers import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Prefetch
from .tasks import send_login_success_email, send_otp_email
import random

def custom_404(request, exception):
    return redirect('home')

@api_view(['POST'])
def create_blog(request):
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class CommentListView(APIView):
    permission_classes = []
    def get(self, request, blog_id=None):
        if blog_id:
            comments = Comment.objects.filter(blog_title__id=blog_id)
        else:
            comments = Comment.objects.all()

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(comment_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(APIView):
    def post(self,request):
        username = request.data.get('username')
        email = request.data.get('email')
        gender = request.data.get('gender')
        age = request.data.get('age')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if user:
            return Response({"error":"Username already exists."},status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create_user(username=username,email=email,gender=gender,age=age,password=password)

        return Response({"message":"Registration Sucessfully"},status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            tokens = get_tokens_for_user(user)  
            return Response({"message": "Login Successfully", "tokens": tokens}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    def post(self,request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"message": "Invalid token format."}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_header.split(' ')[1]
        logout(request)

        return Response({"message": "Logout Successfully"}, status=status.HTTP_200_OK)

class Blogviewset(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

class Bloggerviewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = BloggerSerializer


def home(request):
    blogs = Blog.objects.select_related('blogger_name').order_by('-post_date')[:3]

    blog = Blog.objects.all().count
    comment = Comment.objects.all().count
    blogger = CustomUser.objects.all().count

    context = {'header' :'Blog App','blogs':blogs,'blog':blog,'comment':comment,'blogger':blogger}
    return render(request,"home.html", context)

def blogs(request):
    blogs = Blog.objects.select_related('blogger_name').order_by('-post_date')

    paginator = Paginator(blogs, 5)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)

    context = {'header' :'Blogs','blogs':blogs}
    return render(request,"blogs.html", context)

def blog_detail(request,id):
    blog = Blog.objects.select_related('blogger_name')\
    .prefetch_related(
        Prefetch('commnettitle',queryset=Comment.objects.select_related('comment_by'))
    )\
    .get(id=id)
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

@login_required(login_url='login_page')
def comment_page(request, id):
    blog = Blog.objects.filter(id=id).first()

    if request.method == "POST":
        comment_detail = request.POST.get('comment_detail')
        user = request.user

        if comment_detail:
            Comment.objects.create(blog_title=blog, comment_detail=comment_detail, comment_by=user)
            return redirect('blog_detail', id=blog.id)

    return render(request, "comment_page.html", {'blog': blog})

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

    next_url = request.GET.get('next', '/')
    
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            send_login_success_email.delay(user.email, user.username)
            return redirect(next_url) 
        else:
            messages.warning(request, 'Invalid email or password.')
            return render(request, 'login_page.html')

    context = {'header' :'Login'}
    return render(request,"login_page.html", context)

def logout_page(request):
    logout(request)
    return redirect('login_page')

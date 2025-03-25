from django.contrib import admin
from django.urls import path,include
from blogger.views import *

urlpatterns = [
    path('', home,name="home"),
    path('blog/', home,name="home"),
    path('register_page/', register_page,name="register_page"),
    path('login_page/', login_page,name="login_page"),
    path('logout_page/', logout_page,name="logout_page"),
    path('blog/blogs/', blogs,name="blogs"),
    path('blog/<int:id>', blog_detail,name="blog_detail"),
    path('blog/bloggers/', bloggers,name="bloggers"),
    path('blog/blogger/<uuid:id>', blogger_detail,name="blogger_detail"),
    
    path('admin/', admin.site.urls),
]
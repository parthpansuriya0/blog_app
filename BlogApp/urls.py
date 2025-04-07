from django.contrib import admin
from django.urls import path,include
from blogger.views import *
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('blogger.urls')),

    path('', home,name="home"),
    path('blog/', home,name="home"),
    path('register_page/', register_page,name="register_page"),
    path('login_page/', login_page,name="login_page"),
    path('logout_page/', logout_page,name="logout_page"),
    path('blog/blogs/', blogs,name="blogs"),
    path('blog/<int:id>', blog_detail,name="blog_detail"),
    path('blog/bloggers/', bloggers,name="bloggers"),
    path('blog/blogger/<uuid:id>', blogger_detail,name="blogger_detail"),
    path('blog/<int:id>/create/', comment_page, name='comment_page'),
]

if not settings.TESTING:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

handler404 = 'blogger.views.custom_404'
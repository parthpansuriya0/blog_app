from django.urls import path,include
from blogger.views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'bloggs',Blogviewset)
router.register(r'bloggers',Bloggerviewset)

urlpatterns = [

    path('', include(router.urls)),
    path('register', RegistrationView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('create_blog', create_blog),
    path('get_comment', CommentListView.as_view()),
    path('get_comment/<blog_id>', CommentListView.as_view()),
    path('create_comment', CreateCommentView.as_view()),

    
]
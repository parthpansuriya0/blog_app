from django.test import TestCase,Client
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from blogger.models import Blog,Comment,CustomUser
from django.contrib.auth.models import Permission
from model_bakery import baker
from unittest.mock import patch , MagicMock

# django-rest-framework-api-testcases
class UserRegistrationTestCase(APITestCase):
    @patch('blogger.views.CustomUser.objects.create_user')
    def test_user_registration(self,mock_create_user):
        mock_create_user.return_value = baker.make(CustomUser)
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "gender": "Male",
            "age": 25,
            "password": "12300"
        }

        response = self.client.post("/api/register", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("registration : OK")

class LoginTestCase(APITestCase):

    def setUp(self):
        self.user = baker.make(CustomUser, email="newuser@example.com", username="newuser")
        self.user.set_password("12300")
        self.user.save()

    @patch('blogger.views.authenticate')
    @patch('blogger.views.get_tokens_for_user')
    def test_login_success(self, mock_get_tokens, mock_auth):

        mock_auth.return_value = self.user
        mock_get_tokens.return_value = {"access": "mock_access", "refresh": "mock_refresh"}

        data = {
            "email": "newuser@example.com",
            "password": "12300"
        }

        response = self.client.post("/api/login", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        print("Login Success : OK" )

    @patch('blogger.views.CustomUser.objects.filter')
    def test_login_invalid_email(self, mock_filter):
        mock_filter.return_value.exists.return_value = False

        data = {"email": "wrong@example.com","password": "12300"}
        response = self.client.post("/api/login", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Login Email check : OK" )

    @patch('blogger.views.authenticate')
    def test_login_invalid_password(self, mock_auth):
        mock_auth.return_value = None

        data = {"email": "newuser@example.com", "password": "wrongpassword"}
        response = self.client.post("/api/login", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Login password check : OK" )

class LogoutTestCase(APITestCase):

    def setUp(self):
        self.user = baker.make(CustomUser, email="test@example.com", username="testuser")
        self.user.set_password("12300")
        self.user.save()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    @patch('blogger.views.logout')
    def test_logout_success(self, mock_logout):
        response = self.client.post("/api/logout", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        mock_logout.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Logout Success : OK" )

    def test_logout_without_token(self):
        response = self.client.post("/api/logout")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Logout without token : OK" )

    def test_logout_with_invalid_token_format(self):
        response = self.client.post("/api/logout", HTTP_AUTHORIZATION="InvalidTokenFormat")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Logout invalid token : OK" )

class BlogTestCase(APITestCase):

    def setUp(self):
        self.user = baker.make(CustomUser, email="test@example.com", username="testuser")
        self.user.set_password("12300")
        self.user.save()

        permissions = ["add_blog", "change_blog", "delete_blog", "view_blog"]
        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            self.user.user_permissions.add(permission)

        self.blog = baker.make(Blog, blogger_name=self.user, title="Test Blog")
        response = self.client.post("/api/login", {"email": "test@example.com", "password": "12300"}, format="json")
        self.token = response.data.get("tokens", {}).get("access", "")

    @patch('blogger.views.Blog.objects.all')
    def test_get_all_blogs(self,mock_all):
        mock_all.return_value = [self.blog]
        response = self.client.get("/api/bloggs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blogs view : OK" )
    
    @patch('blogger.views.BlogSerializer.save')
    def test_create_blog(self,mock_save):
        blog_data = {"title": "New Blog","content": "New blog content","author_name": "Jane Doe","blogger_name": self.user.id }
        mock_save.return_value = None
        response = self.client.post("/api/bloggs/", blog_data, format="json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Blogs create : OK" )

    @patch('blogger.views.Blog.objects.get')
    def test_get_single_blog(self,mock_get):
        mock_get.return_value = self.blog
        response = self.client.get(f"/api/bloggs/{self.blog.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blog view : OK" )

    @patch('blogger.views.Blog.objects.get')
    def test_update_blog(self,mock_get):
        mock_get.return_value = self.blog
        updated_data = {"title": "Updated Blog","content": "Updated blog content","author_name": "John Smith","blogger_name": self.user.id}
        response = self.client.put(f"/api/bloggs/{self.blog.id}/", updated_data, format="json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blog update : OK" )

    @patch('blogger.views.Blog.objects.get')
    def test_delete_blog(self,mock_get):
        mock_blog = MagicMock()
        mock_blog.delete.return_value = None
        mock_get.return_value = mock_blog
        response = self.client.delete(f"/api/bloggs/{self.blog.id}/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print("Blog delete : OK" )

    def test_create_blog_missing_title(self):
        blog_data = {"content": "Missing title", "author_name": "Author", "blogger_name": self.user.id}
        response = self.client.post("/api/bloggs/", blog_data, format="json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Blog missing title : OK")

class BloggerTestCase(APITestCase):

    def setUp(self):
        self.user = baker.make(CustomUser, email="blogger@example.com", username="bloggertest")
        self.user.set_password("12300")
        self.user.save()

    @patch('blogger.views.CustomUser.objects.all')
    def test_get_all_bloggers(self,mock_all):
        mock_all.return_value = [self.user]
        response = self.client.get("/api/bloggers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Bloggers view : OK" )

    @patch('blogger.views.CustomUser.objects.get')
    def test_get_single_blogger(self,mock_get):
        mock_get.return_value = self.user
        response = self.client.get(f"/api/bloggers/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blogger view : OK" )

class CommentTestCase(APITestCase):

    def setUp(self):
        self.user = baker.make(CustomUser, email="test@example.com", username="testuser")
        self.user.set_password("12300")
        self.user.save()
        self.blog = baker.make(Blog, blogger_name=self.user, title="Test Blog")
        login_data = {"email": "test@example.com", "password": "12300"}
        response = self.client.post("/api/login", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data, "Login response does not contain tokens")
        self.token = response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.comment = baker.make(Comment, blog_title=self.blog, comment_detail="This is a test comment.", comment_by=self.user)
    
    @patch('blogger.views.CommentSerializer.save')
    def test_create_comment(self, mock_save):

        comment_data = {
            "blog_title": self.blog.id,
            "comment_detail": "This is a test comment.",
            "comment_by": self.user.id
        }
        mock_save.return_value = None
        response = self.client.post("/api/create_comment", comment_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment_detail"], "This is a test comment.")
        self.assertEqual(response.data["blog_title"], self.blog.id)
        self.assertEqual(response.data["comment_by"], self.user.id)
        print("Comment create : OK" )
    
    def test_create_comment_without_authentication(self):
        self.client.credentials()   

        comment_data = {
            "blog_title": self.blog.id,
            "comment_detail": "This comment should fail.",
        }

        response = self.client.post("/api/create_comment", comment_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("Comment create without authentication : OK" )

    @patch('blogger.views.Comment.objects.all')
    def test_get_all_comments(self, mock_all):
        mock_all.return_value = [self.comment]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/get_comment/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Comments view : OK" )

    @patch('blogger.views.Comment.objects.filter')
    def test_get_comments_by_blog(self,mock_filter):
        mock_filter.return_value = [self.comment]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(f"/api/get_comment/{self.blog.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Comment by blog view : OK" )

#django-testcases
class BlogAppTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = baker.make(CustomUser, email='test@example.com', username='testuser', gender='Male', age=25)
        self.blog = baker.make(Blog, title='Test Blog', blogger_name=self.user, author_name='John Doe')

    @patch('blogger.views.Blog.objects.select_related')
    def test_home_view(self, mock_blog_queryset):
        mock_blog_queryset.return_value.order_by.return_value = []
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("Home view : OK" )
    
    def test_blogs_view(self):
        response = self.client.get('/blog/blogs/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs.html')
        print("Blogs view : OK" )
    
    def test_blog_detail_view(self):
        response = self.client.get(f'/blog/{self.blog.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_detail.html')
        print("Blog detail view : OK" )
    
    def test_bloggers_view(self):
        response = self.client.get('/blog/bloggers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bloggers.html')
        print("Bloggers view : OK" )
    
    def test_blogger_detail_view(self):
        response = self.client.get(f'/blog/blogger/{self.user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogger_detail.html')
        print("Blogger detail view : OK" )
    
    def test_register_view(self):
        response = self.client.post('/register_page/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'gender': 'Female',
            'age': 30,
            'password': 'testpass123',
            'confirm_password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(CustomUser.objects.filter(email='newuser@example.com').exists())
        print("Register view : OK" )
    
    def test_login_view(self):
        login_user = baker.make(CustomUser, email='testuser@example.com', password='testpassword123', username='testuser', gender='Male', age=25)
        login_user.set_password('testpassword123')
        login_user.save()
        login_url = '/login_page/'

        response = self.client.post(login_url, {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)
        print("Login view : OK")
    
    def test_logout_view(self):
        self.user.set_password('password123')
        self.user.save()
        self.client.login(email='test@example.com', password='password123')
        response = self.client.get('/logout_page/')
        self.assertEqual(response.status_code, 302)
        print("Logout view : OK" )
    
class CommentPageTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = baker.make(CustomUser, email='testuser@example.com', username='testuser', gender='Male', age=25)
        self.user.set_password('testpassword123')
        self.user.save()

        self.blog = baker.make(Blog, blogger_name=self.user, title='Test Blog', author_name='John Doe')

        self.comment_url = f'/blog/{self.blog.id}/create/'

    def test_comment_page_requires_login(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.url.startswith('/login_page/'))
        print("Comment page requires login : OK" )  

    def test_comment_submission(self):
        self.client.login(email='testuser@example.com', password='testpassword123')

        response = self.client.post(self.comment_url, {
            'comment_detail': 'This is a test comment.'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(comment_detail='This is a test comment.').exists())
        print("Comment submission : OK" )

    def test_empty_comment_not_created(self):
        self.client.login(email='testuser@example.com', password='testpassword123')

        response = self.client.post(self.comment_url, {
            'comment_detail': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.exists())
        print("Empty comment not created : OK" )

    def test_comment_saved_with_correct_user_and_blog(self):
        self.client.login(email='testuser@example.com', password='testpassword123')

        response = self.client.post(self.comment_url, {
            'comment_detail': 'Another test comment.'
        })

        self.assertEqual(response.status_code, 302)

        comment = Comment.objects.get(comment_detail='Another test comment.')
        self.assertEqual(comment.comment_by, self.user)
        self.assertEqual(comment.blog_title, self.blog)
        print("Comment saved with correct user and blog : OK" )

from django.test import TestCase,Client
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from blogger.models import Blog,Comment,CustomUser
from django.contrib.auth.models import Permission

# django-rest-framework-api-testcases
class UserRegistrationTestCase(APITestCase):
    def test_user_registration(self):
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
        self.user = CustomUser.objects.create_user(
            email="newuser@example.com",
            username="newuser",
            password="12300",
            gender="Male",
            age=25
        )

    def test_login_success(self):
        data = {
            "email": "newuser@example.com",
            "password": "12300"
        }

        response = self.client.post("/api/login", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        print("Login Success : OK" )

    def test_login_invalid_email(self):
        data = {
            "email": "wrong@example.com",
            "password": "12300"
        }

        response = self.client.post("/api/login", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Login Email check : OK" )

    def test_login_invalid_password(self):
        data = {
            "email": "newuser@example.com",
            "password": "wrongpassword"
        }

        response = self.client.post("/api/login", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print("Login password check : OK" )

class LogoutTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="12300",
            gender="Male",
            age=25
        )

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def test_logout_success(self):
        response = self.client.post("/api/logout", HTTP_AUTHORIZATION=f"Bearer {self.token}")

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
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="12300",
            gender="Male",
            age=25
        )

        permissions = [
            "add_blog",
            "change_blog",
            "delete_blog",
            "view_blog"
        ]
        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            self.user.user_permissions.add(permission)

        self.user.save()

        self.blog = Blog.objects.create(
            title="Test Blog",
            content="This is a test blog.",
            author_name="John Doe",
            blogger_name=self.user
        )

        response = self.client.post("/api/login", {"email": "test@example.com", "password": "12300"}, format="json")
        self.token = response.data.get("tokens", {}).get("access", "")

    def test_get_all_blogs(self):
        response = self.client.get("/api/bloggs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blogs view : OK" )
    
    def test_create_blog(self):
        blog_data = {"title": "New Blog","content": "New blog content","author_name": "Jane Doe","blogger_name": self.user.id }
        response = self.client.post("/api/bloggs/", blog_data, format="json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Blogs create : OK" )

    def test_get_single_blog(self):
        response = self.client.get(f"/api/bloggs/{self.blog.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blog view : OK" )

    def test_update_blog(self):
        updated_data = {"title": "Updated Blog","content": "Updated blog content","author_name": "John Smith","blogger_name": self.user.id}
        response = self.client.put(f"/api/bloggs/{self.blog.id}/", updated_data, format="json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blog update : OK" )

    def test_delete_blog(self):
        response = self.client.delete(f"/api/bloggs/{self.blog.id}/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        print("Blog delete : OK" )

class BloggerTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="blogger@example.com",
            username="bloggertest",
            password="12300",
            gender="Male",
            age=30
        )

    def test_get_all_bloggers(self):
        response = self.client.get("/api/bloggers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Bloggers view : OK" )

    def test_get_single_blogger(self):
        response = self.client.get(f"/api/bloggers/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Blogger view : OK" )

class CommentTestCase(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="12300",
            gender="Male",
            age=25
        )

        self.blog = Blog.objects.create(
            title="Test Blog",
            content="This is a test blog content.",
            author_name="John Doe",
            blogger_name=self.user
        )

        login_data = {"email": "test@example.com", "password": "12300"}
        response = self.client.post("/api/login", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data, "Login response does not contain tokens")

        self.token = response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.comment = Comment.objects.create(
            blog_title=self.blog,
            comment_detail="This is a test comment.",
            comment_by=self.user
        )
    
    def test_create_comment(self):
        comment_data = {
            "blog_title": self.blog.id,
            "comment_detail": "This is a test comment.",
            "comment_by": self.user.id
        }

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

    def test_get_all_comments(self):
        Comment.objects.create(blog_title=self.blog, comment_detail="Test Comment", comment_by=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get("/api/get_comment/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Comments view : OK" )

    def test_get_comments_by_blog(self):
        Comment.objects.create(blog_title=self.blog, comment_detail="Specific Blog Comment", comment_by=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(f"/api/get_comment/{self.blog.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Comment by blog view : OK" )

#django-testcases
class BlogAppTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='12300', gender='Male', age=25
        )
        self.blog = Blog.objects.create(
            title='Test Blog',
            content='This is a test blog content.',
            author_name='John Doe',
            blogger_name=self.user
        )

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
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
        self.client = Client()
        self.login_url = '/login_page/'

        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            gender='Male',
            age=25
        )

        response = self.client.post(self.login_url, {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)
        print("Login view : OK")
    
    def test_logout_view(self):
        self.client.login(email='test@example.com', password='password123')
        response = self.client.get('/logout_page/')
        self.assertEqual(response.status_code, 302)
        print("Logout view : OK" )
    
class CommentPageTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            gender='Male',
            age=25
        )

        self.blog = Blog.objects.create(
            title='Test Blog',
            content='This is a test blog content.',
            author_name='John Doe',
            blogger_name=self.user
        )

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

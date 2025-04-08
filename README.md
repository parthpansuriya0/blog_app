# 📰 BlogApp

A blog application built with Django and Django REST Framework, featuring authentication, user profiles, blogs, and comments.

## 🚀 Features

- ✅ Custom user model with UUID, email as username, gender, and age fields
- ✅ JWT Authentication with SimpleJWT
- ✅ Create, view, and manage blog posts
- ✅ Add comments to blog posts
- ✅ Blogger profile system
- ✅ Django Admin dashboard
- ✅ Pagination and permissions with DRF
- ✅ Debug Toolbar for development
- ✅ SQLite for local dev

## Tech Stack

- Django
- Django REST Framework
- SimpleJWT
- SQLite
- Model Bakery (tests)

## Setup

1. **Clone the repo**
    ```bash
    git clone https://github.com/parthpansuriya0/blog_app.git
    ```
2. **Create a virtual environment**
   - **Windows:**
     ```bash
     python -m venv venv
     ```

   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     ```

3. **Activate the virtual environment**

    - On **Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - On **Linux/macOS**:
      ```bash
      source venv/bin/activate
      ```

4. **Install dependencies**

     ```bash
     pip install -r requirements.txt
     ```


5. **Run migrations**

   - **Windows:**
     ```bash
     python manage.py migrate
     ```

   - **macOS / Linux:**
     ```bash
     python3 manage.py migrate
     ```

6. **Start the server**

   - **Windows:**
     ```bash
     python manage.py runserver
     ```

   - **macOS / Linux:**
     ```bash
     python3 manage.py runserver
     ```

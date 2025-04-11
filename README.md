# Noctra Backend

Noctra is a modern social media platform built with Django REST Framework. It allows users to manage posts, upload media, and update profile details. This README provides an overview of the backend setup, database configuration, and instructions for running the server.

## Features
- User registration and authentication (using JWT tokens)
- Create, edit, and delete posts
- Upload and manage media (images, videos, audio, documents)
- Edit user profile details

## Technologies Used
- **Backend**: Django with Django REST Framework
- **Database**: PostgreSQL (or any other supported database)
- **Authentication**: JWT (JSON Web Token)
- **File Storage**: Local or Cloud (e.g., AWS S3)

## Getting Started

### Prerequisites
Before setting up the backend, ensure that you have the following installed:
- **Python** (v3.8 or higher)
- **Django** (v3.2 or higher)
- **PostgreSQL** (or any other supported database)

### Setup

#### 1. Clone the repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Riddimental/Backend_Noctra.git
cd noctra
```

#### 2. Backend Setup

Navigate to the backend directory and create a virtual environment:

```bash
cd noctra_backend
python3 -m venv venv
```

Activate the virtual environment:

- On Linux/macOS:

```bash
source venv/bin/activate
```

- On Windows:

```bash
venv\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

#### 3. Database Setup

Create the database and apply migrations:

```bash
python3 manage.py makemigrations noctra_app
python3 manage.py migrate
```

Create a superuser for the admin interface:

```bash
python3 manage.py createsuperuser
```

Provide your username, email (optional), and password for the superuser.

#### 4. Static Files and Media (optional)
If you're serving static files and media (e.g., profile pictures, uploaded media), ensure you configure your `settings.py` appropriately.

For local development, you can add the following settings:

```python
# In settings.py
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```

Run the collectstatic command to gather static files:

```bash
python3 manage.py collectstatic
```

### Backend Execution

After the dependencies are installed and migrations are applied, you can run the Django development server:

```bash
python3 manage.py runserver
```

The backend should now be running on [http://127.0.0.1:8000](http://127.0.0.1:8000). You can access the Django admin interface at:

[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

Use the superuser credentials you created earlier to log in and manage the application.

### API Documentation

The backend exposes the following API endpoints (details may vary depending on your application):

- **POST /api/auth/register/**: User registration endpoint
- **POST /api/auth/token/**: Obtain JWT token for authentication
- **GET /api/posts/**: Retrieve all posts
- **POST /api/posts/**: Create a new post
- **PATCH /api/posts/{id}/**: Update a specific post
- **DELETE /api/posts/{id}/**: Delete a specific post
- **GET /api/userprofiles/me/**: Get the current user's profile information
- **PATCH /api/userprofiles/me/**: Update the current user's profile information

Make sure to replace API details according to your actual implementation.

## Licenses

This project is licensed under the MIT License - see the LICENSE file for details.

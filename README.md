# Noctra Backend

Noctra is a modern social media platform built using **Django REST Framework**. It allows users to create and manage posts, upload media, and update their profiles. This README provides an overview of the backend setup, configuration, and instructions for running the server.

## Features

- User registration and authentication using **JWT tokens**.
- Create, edit, and delete posts.
- Upload and manage media (images, videos, audio, documents).
- Edit user profile details.
- Handle **mentions** in captions (using `@username`).
- Tagging functionality for posts.
  
## Technologies Used

- **Backend**: Django with Django REST Framework
- **Database**: PostgreSQL (or any other supported database)
- **Authentication**: JWT (JSON Web Token)
- **File Storage**: Local or Cloud (e.g., AWS S3)
- **File Upload**: MultiPartParser for handling media files

## Getting Started

### Prerequisites
Before setting up the backend, ensure that you have the following installed:
- **Python** (v3.8 or higher)
- **Django** (v3.2 or higher)
- **PostgreSQL** (or any other supported database)

### Setup

#### 1. Clone the Repository

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

#### 4. Static Files and Media (Optional)
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

### Authentication

All API requests **require a valid JWT token** for authentication. You can obtain the token by making a POST request to the following endpoint after registering a user:

- **POST** `/api/auth/token/`: Obtain a JWT token for authentication.
  - Pass the username and password to receive the token.
  
Use the token by including it in the Authorization header:

```
Authorization: Bearer <your_token>
```

### API Endpoints

Here are the key API endpoints available for use:

- **POST /api/auth/register/**: User registration endpoint (to create a new user).
- **POST /api/auth/token/**: Obtain JWT token for authentication.
- **GET /api/posts/**: Retrieve all posts (supports pagination).
- **POST /api/posts/**: Create a new post.
  - Include `caption`, `tags`, `media`, and `mentions` (as JSON array).
  - **Mentions**: Use `@username` in captions or send a list of user IDs in the request.
- **PATCH /api/posts/{id}/**: Update a specific post.
  - You can update the caption, tags, and mentions of a post.
- **DELETE /api/posts/{id}/**: Delete a specific post.
- **GET /api/posts/{id}/**: Retrieve details of a specific post.
- **GET /api/userprofiles/me/**: Get the current user's profile information.
- **PATCH /api/userprofiles/me/**: Update the current user's profile information.
  
Make sure to replace these endpoints according to your actual implementation details.

### Media Upload

The API allows users to upload media with their posts. Supported media types include:

- **Images** (JPEG, PNG, GIF)
- **Videos** (MP4, MOV, AVI)
- **Audio** (MP3, WAV)
- **Documents** (PDF, DOCX)

To upload media, use the **POST /api/posts/** endpoint and include the files in the request body as `media` (handled as multi-part form data).

### Example Post Creation

To create a post with mentions and tags:

```bash
curl -X POST \
  http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer <your_token>" \
  -F "caption=Check out this #amazing post with @user1 and @user2!" \
  -F "tags=[{'name': 'amazing'}]" \
  -F "media=@/path/to/file.jpg"
```

## Licenses

This project is licensed under the [Proprietary License](LICENSE) - all rights reserved. This project is an independent work and is not affiliated with any institution.

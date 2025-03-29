from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import uuid

class MediaStorageAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    # Define the base path for media storage
    media_base_path = os.path.join(settings.BASE_DIR, 'media')

    def post(self, request):
        if request.method == 'POST':
            file = request.FILES['file']
            file_type = request.data.get('file_type', 'images')  # Default to 'images' if not provided
            file_category = request.data.get('file_category', 'posts')  # Default to 'posts' if not provided

            # Validate the file_type and file_category (to prevent unwanted uploads)
            if file_type not in ['images', 'videos', 'other']:
                return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
            if file_category not in ['profile_pictures', 'cover_pictures', 'posts', 'stories', 'audios', 'documents', 'profile_videos']:
                return Response({'error': 'Invalid file category'}, status=status.HTTP_400_BAD_REQUEST)

            # Dynamically create the directory path based on the file type and category
            media_dir = os.path.join(self.media_base_path, file_type, file_category)

            # Ensure the directory exists
            os.makedirs(media_dir, exist_ok=True)

            # Generate a unique filename (to avoid name conflicts)
            file_extension = os.path.splitext(file.name)[1]  # Extract file extension (e.g., '.jpg')
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"  # Unique file name

            # Save the file
            fs = FileSystemStorage(location=media_dir)
            filename = fs.save(unique_filename, file)
            
            # Generate the URL for the uploaded file
            file_url = os.path.join('/media', file_type, file_category, filename)

            # Return the URL of the uploaded file
            return Response({'file_url': file_url}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.method == 'GET':
            file_url = request.GET.get('file_url')
            if not file_url:
                return Response({'error': 'file_url parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'file_url': file_url}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

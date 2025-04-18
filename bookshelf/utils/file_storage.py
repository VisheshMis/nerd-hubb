import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'epub', 'mobi', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    """Check if a file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, user_id):
    """
    Save an uploaded file and return file metadata
    
    Args:
        file: The file object from request.files
        user_id: The ID of the user uploading the file
        
    Returns:
        dict: Metadata for the saved file or None if the file is invalid
    """
    if not file or not allowed_file(file.filename):
        return None
    
    # Use a UUID for the filename to avoid collisions
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    new_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Create the upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.instance_path, 'uploads', 'books', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)
    
    # Determine the file type
    file_type = file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
    
    # Get the file size
    file_size = os.path.getsize(file_path)
    
    # Create the file metadata
    file_metadata = {
        'original_filename': original_filename,
        'filename': new_filename,
        'file_path': os.path.join('uploads', 'books', str(user_id), new_filename),
        'file_size': file_size,
        'file_type': file_type
    }
    
    return file_metadata

def delete_file(file_path):
    """
    Delete a file at the given path
    
    Args:
        file_path: The path to the file relative to the instance folder
        
    Returns:
        bool: True if the file was deleted, False otherwise
    """
    full_path = os.path.join(current_app.instance_path, file_path)
    
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    return False 
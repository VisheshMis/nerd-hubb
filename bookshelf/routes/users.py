from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_from_directory, Response, current_app
from flask_login import current_user, login_required
from bookshelf.app import db
from bookshelf.models import User, Review, Book, Shelf, BookFile
from bookshelf.forms.users import ProfileForm
from bookshelf.forms.books import BookFileUploadForm
from bookshelf.utils.file_storage import save_file, delete_file
import os
import mimetypes

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/<username>')
def profile(username):
    """View a user's profile"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get counts for shelves
    shelf_counts = {
        'want_to_read': Shelf.query.filter_by(user_id=user.id, status='want_to_read').count(),
        'reading': Shelf.query.filter_by(user_id=user.id, status='reading').count(),
        'read': Shelf.query.filter_by(user_id=user.id, status='read').count()
    }
    
    # Get recent activity (reviews)
    recent_reviews = Review.query.filter_by(user_id=user.id).order_by(
        Review.created_at.desc()
    ).limit(5).all()
    
    # Is the current user following this user?
    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(user)
    
    return render_template('users/profile.html',
                          user=user,
                          shelf_counts=shelf_counts,
                          recent_reviews=recent_reviews,
                          is_following=is_following)

@users_bp.route('/<username>/shelves/<string:status>')
def shelves(username, status):
    """View a specific shelf for a user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if status not in ['want_to_read', 'reading', 'read']:
        abort(404)
    
    # Get shelf counts
    shelf_counts = {
        'want_to_read': Shelf.query.filter_by(user_id=user.id, status='want_to_read').count(),
        'reading': Shelf.query.filter_by(user_id=user.id, status='reading').count(),
        'read': Shelf.query.filter_by(user_id=user.id, status='read').count()
    }
    
    # Get books on this shelf with pagination
    page = request.args.get('page', 1, type=int)
    shelf_books = db.session.query(Book, Shelf).join(
        Shelf, Shelf.book_id == Book.id
    ).filter(
        Shelf.user_id == user.id,
        Shelf.status == status
    ).order_by(Shelf.date_added.desc()).paginate(page=page, per_page=12)
    
    return render_template('users/shelves.html',
                          user=user,
                          shelf_status=status,
                          shelf_books=shelf_books,
                          shelf_counts=shelf_counts)

@users_bp.route('/<username>/reviews')
def reviews(username):
    """View all reviews by a user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(user_id=user.id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('users/reviews.html',
                          user=user,
                          reviews=reviews)

@users_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Edit user profile settings"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        # Handle profile picture upload (simplified for now)
        if form.profile_pic_url.data:
            current_user.profile_pic_url = form.profile_pic_url.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    
    return render_template('users/settings.html', form=form)

@users_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """Follow a user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if user == current_user:
        flash('You cannot follow yourself!', 'danger')
        return redirect(url_for('users.profile', username=username))
    
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!', 'success')
    
    return redirect(url_for('users.profile', username=username))

@users_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """Unfollow a user"""
    user = User.query.filter_by(username=username).first_or_404()
    
    if user == current_user:
        flash('You cannot unfollow yourself!', 'danger')
        return redirect(url_for('users.profile', username=username))
    
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {username}.', 'success')
    
    return redirect(url_for('users.profile', username=username))

@users_bp.route('/<username>/files')
def files(username):
    """View a user's uploaded book files"""
    user = User.query.filter_by(username=username).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    files = BookFile.query.filter_by(user_id=user.id).order_by(
        BookFile.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('users/files.html',
                          user=user,
                          files=files)

@users_bp.route('/files/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Upload a book file"""
    form = BookFileUploadForm()
    
    # Populate book choices
    books = Book.query.order_by(Book.title).all()
    form.book.choices = [(0, 'None')] + [(book.id, f"{book.title} by {book.author}") for book in books]
    
    if form.validate_on_submit():
        file = request.files['file']
        
        if file:
            # Save the file and get metadata
            file_metadata = save_file(file, current_user.id)
            
            if file_metadata:
                # Create a new BookFile record
                book_file = BookFile(
                    filename=file_metadata['filename'],
                    original_filename=file_metadata['original_filename'],
                    file_path=file_metadata['file_path'],
                    file_size=file_metadata['file_size'],
                    file_type=file_metadata['file_type'],
                    description=form.description.data,
                    user_id=current_user.id
                )
                
                # Link to a book if selected
                if form.book.data != 0:
                    book_file.book_id = form.book.data
                
                db.session.add(book_file)
                db.session.commit()
                
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('users.files', username=current_user.username))
            else:
                flash('Error saving file. Please try again.', 'danger')
        else:
            flash('No file selected.', 'danger')
    
    return render_template('users/upload_file.html', form=form)

@users_bp.route('/files/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_book_file(file_id):
    """Delete a book file"""
    book_file = BookFile.query.get_or_404(file_id)
    
    # Check if the current user owns the file
    if book_file.user_id != current_user.id:
        abort(403)
    
    # Delete the physical file
    if delete_file(book_file.file_path):
        # Delete the database record
        db.session.delete(book_file)
        db.session.commit()
        flash('File deleted successfully!', 'success')
    else:
        flash('Error deleting file. The database record was not removed.', 'danger')
    
    return redirect(url_for('users.files', username=current_user.username))

@users_bp.route('/files/<int:file_id>/download')
def download_file(file_id):
    """Download a file"""
    book_file = BookFile.query.get_or_404(file_id)
    
    # Get the directory and filename
    file_dir = os.path.dirname(os.path.join(current_app.instance_path, book_file.file_path))
    filename = os.path.basename(book_file.file_path)
    
    return send_from_directory(
        file_dir, 
        filename,
        as_attachment=True,
        download_name=book_file.original_filename
    )

@users_bp.route('/files/<int:file_id>/read')
def read_file(file_id):
    """Display a book file for reading"""
    book_file = BookFile.query.get_or_404(file_id)
    
    # Get the absolute file path
    absolute_file_path = os.path.join(current_app.instance_path, book_file.file_path)
    
    # Choose template based on file type
    if book_file.file_type == 'application/pdf':
        return render_template('users/read_pdf.html', book_file=book_file)
    elif 'epub' in book_file.file_type:
        return render_template('users/read_epub.html', book_file=book_file)
    elif 'text/plain' in book_file.file_type:
        # For text files, read the content
        try:
            with open(absolute_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return render_template('users/read_text.html', book_file=book_file, content=content)
        except Exception as e:
            flash(f'Error reading file: {str(e)}', 'danger')
            return redirect(url_for('users.files', username=current_user.username))
    else:
        # For unsupported file types
        flash('This file type is not supported for online reading. Please download the file.', 'warning')
        return redirect(url_for('users.files', username=current_user.username))

@users_bp.route('/files/<int:file_id>/stream')
def stream_file(file_id):
    """Stream a file for online reading"""
    book_file = BookFile.query.get_or_404(file_id)
    
    # Get the file path
    file_path = os.path.join(current_app.instance_path, book_file.file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        abort(404)
    
    # Determine content type
    content_type = book_file.file_type
    if not content_type or content_type == 'application/octet-stream':
        content_type, _ = mimetypes.guess_type(book_file.original_filename)
        if not content_type:
            content_type = 'application/octet-stream'
    
    # Stream the file
    def generate():
        with open(file_path, 'rb') as f:
            yield from f
    
    return Response(generate(), mimetype=content_type) 
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from bookshelf.app import db
from bookshelf.models import Book, Shelf, User
from datetime import datetime

shelves_bp = Blueprint('shelves', __name__, url_prefix='/shelves')

@shelves_bp.route('/')
@login_required
def index():
    """Show the current user's bookshelves"""
    # Get counts for each shelf status
    want_count = Shelf.query.filter_by(user_id=current_user.id, status='want_to_read').count()
    reading_count = Shelf.query.filter_by(user_id=current_user.id, status='reading').count()
    read_count = Shelf.query.filter_by(user_id=current_user.id, status='read').count()
    
    # Get the requested shelf or default to 'want_to_read'
    shelf_status = request.args.get('status', 'want_to_read')
    if shelf_status not in ['want_to_read', 'reading', 'read']:
        shelf_status = 'want_to_read'
    
    # Get books on the current shelf with pagination
    page = request.args.get('page', 1, type=int)
    shelf_books = db.session.query(Book, Shelf).join(
        Shelf, Shelf.book_id == Book.id
    ).filter(
        Shelf.user_id == current_user.id,
        Shelf.status == shelf_status
    ).order_by(Shelf.date_added.desc()).paginate(page=page, per_page=12)
    
    return render_template('shelves/index.html',
                          shelf_status=shelf_status,
                          shelf_books=shelf_books,
                          want_count=want_count,
                          reading_count=reading_count,
                          read_count=read_count)

@shelves_bp.route('/add/<int:book_id>/<string:status>', methods=['POST'])
@login_required
def add_to_shelf(book_id, status):
    """Add a book to a shelf or change its status"""
    if status not in ['want_to_read', 'reading', 'read']:
        flash('Invalid shelf status.', 'danger')
        return redirect(url_for('books.view', book_id=book_id))
    
    # Check if book exists
    book = Book.query.get_or_404(book_id)
    
    # Check if book is already on a shelf
    shelf = Shelf.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    
    if shelf:
        # Update shelf status
        old_status = shelf.status
        shelf.status = status
        
        # Set date started/finished based on status change
        if old_status != 'reading' and status == 'reading':
            shelf.date_started = datetime.utcnow()
        elif old_status != 'read' and status == 'read':
            shelf.date_finished = datetime.utcnow()
        
        flash(f'Book moved to your "{status}" shelf!', 'success')
    else:
        # Create new shelf entry
        shelf = Shelf(user_id=current_user.id, book_id=book_id, status=status)
        
        # Set date started/finished based on status
        if status == 'reading':
            shelf.date_started = datetime.utcnow()
        elif status == 'read':
            shelf.date_started = datetime.utcnow()
            shelf.date_finished = datetime.utcnow()
            
        db.session.add(shelf)
        flash(f'Book added to your "{status}" shelf!', 'success')
    
    db.session.commit()
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'shelf': status})
    
    return redirect(url_for('books.view', book_id=book_id))

@shelves_bp.route('/remove/<int:book_id>', methods=['POST'])
@login_required
def remove_from_shelf(book_id):
    """Remove a book from all shelves"""
    shelf = Shelf.query.filter_by(user_id=current_user.id, book_id=book_id).first_or_404()
    
    db.session.delete(shelf)
    db.session.commit()
    
    flash('Book removed from your shelves.', 'success')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success'})
    
    return redirect(url_for('books.view', book_id=book_id)) 
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from bookshelf.app import db
from bookshelf.models import Book, Review, Genre, User
from bookshelf.forms.books import BookSearchForm, ReviewForm
import json
from sqlalchemy import or_

books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/')
def index():
    """List books with search and filtering options"""
    form = BookSearchForm()
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Book.query
    
    # Apply search filters if provided
    search = request.args.get('search', '')
    if search:
        query = query.filter(or_(
            Book.title.ilike(f'%{search}%'),
            Book.author.ilike(f'%{search}%')
        ))
    
    # Filter by genre if provided
    genre_id = request.args.get('genre_id', type=int)
    if genre_id:
        query = query.filter(Book.genres.any(id=genre_id))
    
    # Paginate the results
    books = query.order_by(Book.title).paginate(page=page, per_page=12)
    
    # Get all genres for the filter dropdown
    genres = Genre.query.order_by(Genre.name).all()
    
    return render_template('books/index.html',
                          books=books,
                          genres=genres,
                          form=form,
                          search=search,
                          genre_id=genre_id)

@books_bp.route('/<int:book_id>')
def view(book_id):
    """Show a single book with details and reviews"""
    book = Book.query.get_or_404(book_id)
    
    # Get reviews with pagination
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(book_id=book_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=5)
    
    # Get user's review if they have one
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            user_id=current_user.id, book_id=book_id
        ).first()
    
    # Form for adding a new review
    review_form = ReviewForm()
    
    return render_template('books/view.html',
                          book=book,
                          reviews=reviews,
                          review_form=review_form,
                          user_review=user_review)

@books_bp.route('/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    """Add or update a book review"""
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user already has a review for this book
        review = Review.query.filter_by(
            user_id=current_user.id, book_id=book_id
        ).first()
        
        if review:
            # Update existing review
            review.rating = form.rating.data
            review.text = form.text.data
            flash('Your review has been updated!', 'success')
        else:
            # Create new review
            review = Review(
                user_id=current_user.id,
                book_id=book_id,
                rating=form.rating.data,
                text=form.text.data
            )
            db.session.add(review)
            flash('Your review has been added!', 'success')
        
        db.session.commit()
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('books.view', book_id=book_id))

@books_bp.route('/search')
def search():
    """API endpoint for searching books (for AJAX requests)"""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    books = Book.query.filter(or_(
        Book.title.ilike(f'%{query}%'),
        Book.author.ilike(f'%{query}%')
    )).limit(10).all()
    
    results = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'cover_url': book.cover_url,
        'url': url_for('books.view', book_id=book.id)
    } for book in books]
    
    return jsonify(results)

@books_bp.route('/import')
def import_form():
    """Show form for importing books from Open Library"""
    return render_template('books/import.html')

@books_bp.route('/import/search')
def import_search():
    """Search Open Library API for books to import"""
    from bookshelf.utils.open_library import OpenLibraryAPI
    
    query = request.args.get('query', '')
    if not query or len(query) < 2:
        flash('Please enter a search term with at least 2 characters', 'warning')
        return redirect(url_for('books.import_form'))
    
    books = OpenLibraryAPI.search_books(query, limit=20)
    return render_template('books/import_results.html', books=books, query=query)

@books_bp.route('/import/save', methods=['POST'])
@login_required
def import_save():
    """Import selected books from Open Library API to local database"""
    from bookshelf.utils.open_library import OpenLibraryAPI
    
    book_data = request.form.getlist('book_data')
    
    if not book_data:
        flash('No books selected for import', 'warning')
        return redirect(url_for('books.import_form'))
    
    imported_count = 0
    for data_json in book_data:
        try:
            book_data = json.loads(data_json)
            
            # Get additional details if we have an Open Library ID
            if book_data.get('open_library_id'):
                details = OpenLibraryAPI.get_book_details(book_data['open_library_id'])
                if details:
                    book_data.update(details)
            
            OpenLibraryAPI.save_book_to_db(book_data)
            imported_count += 1
            
        except Exception as e:
            flash(f'Error importing book: {str(e)}', 'danger')
            continue
    
    if imported_count > 0:
        flash(f'Successfully imported {imported_count} books!', 'success')
    
    return redirect(url_for('books.index')) 
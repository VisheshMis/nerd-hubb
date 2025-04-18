from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from bookshelf.app import db
from bookshelf.models import Book, Review, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage showing popular books and activity feed for logged-in users"""
    # Get trending books (most reviewed recently)
    trending_books = Book.query.join(Review).order_by(Review.created_at.desc()).limit(6).all()
    
    # For logged-in users, show their feed
    activity_feed = None
    if current_user.is_authenticated:
        activity_feed = current_user.followed_users_activity().limit(10).all()
        
        # If no followed activity, show some recent activity from any users
        if not activity_feed:
            activity_feed = Review.query.order_by(Review.created_at.desc()).limit(10).all()
    
    return render_template('main/index.html', 
                          trending_books=trending_books,
                          activity_feed=activity_feed)

@main_bp.route('/discover')
def discover():
    """Discover page showing curated lists of books"""
    # Get various book lists for discovery
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(8).all()
    
    # Get highest rated books with at least 5 reviews
    top_rated = Book.query.join(Review).group_by(Book.id).having(
        db.func.count(Review.id) >= 5
    ).order_by(db.func.avg(Review.rating).desc()).limit(8).all()
    
    # You could add more categories like genre-specific books, etc.
    
    return render_template('main/discover.html',
                          recent_books=recent_books,
                          top_rated=top_rated)

@main_bp.route('/about')
def about():
    """About page with info about the site"""
    return render_template('main/about.html') 
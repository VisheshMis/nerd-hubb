from bookshelf.app import db
from datetime import datetime

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, index=True)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(256))
    published_date = db.Column(db.Date)
    publisher = db.Column(db.String(100))
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shelves = db.relationship('Shelf', backref='book', lazy='dynamic')
    reviews = db.relationship('Review', backref='book', lazy='dynamic')
    book_files = db.relationship('BookFile', backref='book', lazy='dynamic')
    
    # Genre relationships will be added via a many-to-many relationship
    genres = db.relationship('Genre', secondary='book_genres', backref=db.backref('books', lazy='dynamic'))
    
    def average_rating(self):
        """Calculate the average rating of the book"""
        from sqlalchemy import func
        from bookshelf.models.review import Review
        result = db.session.query(func.avg(Review.rating)).filter(Review.book_id == self.id).scalar()
        return round(result, 1) if result else 0
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Genre {self.name}>'

# Association table for book-genre many-to-many relationship
book_genres = db.Table('book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
) 
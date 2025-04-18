"""
Script to add sample books to the BookShelf database
"""
from bookshelf.app import create_app, db
from bookshelf.models.book import Book, Genre
from datetime import datetime

def add_sample_books():
    """Add sample books to the database"""
    app = create_app()
    with app.app_context():
        # Create all tables in the database
        db.create_all()
        print("Database tables created.")
        
        # Create some genres
        genres = {
            'Fantasy': Genre(name='Fantasy'),
            'Science Fiction': Genre(name='Science Fiction'),
            'Mystery': Genre(name='Mystery'),
            'Romance': Genre(name='Romance'),
            'Thriller': Genre(name='Thriller'),
            'Non-Fiction': Genre(name='Non-Fiction'),
            'Biography': Genre(name='Biography'),
            'History': Genre(name='History'),
            'Young Adult': Genre(name='Young Adult')
        }
        
        # Add genres to database
        for genre_name, genre in genres.items():
            existing = Genre.query.filter_by(name=genre_name).first()
            if not existing:
                db.session.add(genre)
                print(f"Added genre: {genre_name}")
            else:
                print(f"Genre already exists: {genre_name}")
                genres[genre_name] = existing
        
        db.session.commit()
        
        # Sample books
        books = [
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': 'J.K. Rowling',
                'isbn': '9780747532743',
                'description': 'Harry Potter has never even heard of Hogwarts when the letters start dropping on the doormat at number four, Privet Drive...',
                'published_date': datetime(1997, 6, 26).date(),
                'publisher': 'Bloomsbury',
                'cover_url': 'https://covers.openlibrary.org/b/id/10523456-M.jpg',
                'page_count': 223,
                'language': 'en',
                'genres': [genres['Fantasy'], genres['Young Adult']]
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'description': 'A gripping, heart-wrenching, and wholly remarkable tale of coming-of-age in a South poisoned by virulent prejudice...',
                'published_date': datetime(1960, 7, 11).date(),
                'publisher': 'HarperCollins',
                'cover_url': 'https://covers.openlibrary.org/b/id/8231488-M.jpg',
                'page_count': 324,
                'language': 'en',
                'genres': [genres['Mystery']]
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'description': 'Among the seminal texts of the 20th century, Nineteen Eighty-Four is a rare work that grows more haunting as its futuristic purgatory becomes more real...',
                'published_date': datetime(1949, 6, 8).date(),
                'publisher': 'Penguin',
                'cover_url': 'https://covers.openlibrary.org/b/id/8575172-M.jpg',
                'page_count': 328,
                'language': 'en',
                'genres': [genres['Science Fiction']]
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'description': 'Since its immediate success in 1813, Pride and Prejudice has remained one of the most popular novels in the English language...',
                'published_date': datetime(1813, 1, 28).date(),
                'publisher': 'Penguin Classics',
                'cover_url': 'https://covers.openlibrary.org/b/id/11347698-M.jpg',
                'page_count': 435,
                'language': 'en',
                'genres': [genres['Romance']]
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'description': 'The Great Gatsby, F. Scott Fitzgerald\'s third book, stands as the supreme achievement of his career...',
                'published_date': datetime(1925, 4, 10).date(),
                'publisher': 'Scribner',
                'cover_url': 'https://covers.openlibrary.org/b/id/8432047-M.jpg',
                'page_count': 180,
                'language': 'en',
                'genres': [genres['Romance']]
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'isbn': '9780316769488',
                'description': 'The hero-narrator of The Catcher in the Rye is an ancient child of sixteen, a native New Yorker named Holden Caulfield...',
                'published_date': datetime(1951, 7, 16).date(),
                'publisher': 'Little, Brown and Company',
                'cover_url': 'https://covers.openlibrary.org/b/id/8231492-M.jpg',
                'page_count': 277,
                'language': 'en',
                'genres': [genres['Young Adult']]
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780618260300',
                'description': 'In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell...',
                'published_date': datetime(1937, 9, 21).date(),
                'publisher': 'Houghton Mifflin',
                'cover_url': 'https://covers.openlibrary.org/b/id/8406786-M.jpg',
                'page_count': 366,
                'language': 'en',
                'genres': [genres['Fantasy']]
            },
            {
                'title': 'Brave New World',
                'author': 'Aldous Huxley',
                'isbn': '9780060850524',
                'description': 'Brave New World is a dystopian novel by English author Aldous Huxley, written in 1931 and published in 1932...',
                'published_date': datetime(1932, 1, 1).date(),
                'publisher': 'Harper Perennial',
                'cover_url': 'https://covers.openlibrary.org/b/id/6389112-M.jpg',
                'page_count': 288,
                'language': 'en',
                'genres': [genres['Science Fiction']]
            },
            {
                'title': 'The Lord of the Rings',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780618640157',
                'description': 'One Ring to rule them all, One Ring to find them, One Ring to bring them all and in the darkness bind them...',
                'published_date': datetime(1954, 7, 29).date(),
                'publisher': 'Houghton Mifflin',
                'cover_url': 'https://covers.openlibrary.org/b/id/8743574-M.jpg',
                'page_count': 1137,
                'language': 'en',
                'genres': [genres['Fantasy']]
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'isbn': '9780061122415',
                'description': 'Paulo Coelho\'s masterpiece tells the mystical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure...',
                'published_date': datetime(1988, 1, 1).date(),
                'publisher': 'HarperOne',
                'cover_url': 'https://covers.openlibrary.org/b/id/8567846-M.jpg',
                'page_count': 197,
                'language': 'en',
                'genres': [genres['Fantasy']]
            }
        ]
        
        # Add books to database
        for book_data in books:
            # Check if book already exists
            existing = Book.query.filter_by(isbn=book_data['isbn']).first()
            if not existing:
                book = Book(
                    title=book_data['title'],
                    author=book_data['author'],
                    isbn=book_data['isbn'],
                    description=book_data['description'],
                    published_date=book_data['published_date'],
                    publisher=book_data['publisher'],
                    cover_url=book_data['cover_url'],
                    page_count=book_data['page_count'],
                    language=book_data['language']
                )
                
                # Add genres
                for genre in book_data['genres']:
                    book.genres.append(genre)
                
                db.session.add(book)
                print(f"Added: {book.title} by {book.author}")
            else:
                print(f"Already exists: {existing.title} by {existing.author}")
        
        db.session.commit()
        print("Sample books added successfully!")

if __name__ == '__main__':
    add_sample_books() 
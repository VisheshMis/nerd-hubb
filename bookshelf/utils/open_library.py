import requests
import json
from datetime import datetime

# Change this line to avoid circular imports
from flask import current_app

class OpenLibraryAPI:
    """
    Utility class for interacting with the Open Library API
    """
    BASE_URL = "https://openlibrary.org"
    SEARCH_URL = f"{BASE_URL}/search.json"
    BOOK_URL = f"{BASE_URL}/works"
    COVER_URL = "https://covers.openlibrary.org/b"

    @staticmethod
    def search_books(query, limit=20):
        """
        Search for books using the Open Library API
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of book data dictionaries
        """
        params = {
            "q": query,
            "limit": limit,
            "mode": "everything"
        }
        
        try:
            response = requests.get(OpenLibraryAPI.SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for book in data.get("docs", []):
                # Extract relevant book information
                book_data = {
                    "title": book.get("title"),
                    "author": ", ".join(book.get("author_name", ["Unknown"])),
                    "cover_id": book.get("cover_i"),
                    "isbn": book.get("isbn", [""])[0] if book.get("isbn") else "",
                    "published_date": book.get("first_publish_year"),
                    "open_library_id": book.get("key", "").replace("/works/", ""),
                    "language": book.get("language", [""])[0] if book.get("language") else "",
                    "genres": [genre for genre in book.get("subject", [])[:5] if len(genre) < 50]
                }
                
                # Add cover URL if available
                if book_data["cover_id"]:
                    book_data["cover_url"] = f"{OpenLibraryAPI.COVER_URL}/id/{book_data['cover_id']}-M.jpg"
                
                results.append(book_data)
                
            return results
        
        except requests.RequestException as e:
            print(f"Error searching books: {e}")
            return []

    @staticmethod
    def get_book_details(book_id):
        """
        Get detailed information about a book by its Open Library ID
        
        Args:
            book_id (str): Open Library book ID
            
        Returns:
            dict: Book details or None if not found
        """
        try:
            response = requests.get(f"{OpenLibraryAPI.BOOK_URL}/{book_id}.json")
            response.raise_for_status()
            book_data = response.json()
            
            # Get book description
            description = ""
            if "description" in book_data:
                if isinstance(book_data["description"], dict):
                    description = book_data["description"].get("value", "")
                else:
                    description = book_data["description"]
            
            return {
                "open_library_id": book_id,
                "description": description
            }
        
        except requests.RequestException as e:
            print(f"Error getting book details: {e}")
            return None

    @staticmethod
    def save_book_to_db(book_data):
        """
        Save book data to the database
        
        Args:
            book_data (dict): Book data from Open Library API
            
        Returns:
            Book: The saved book object
        """
        # Import here to avoid circular imports
        from bookshelf.app import db
        from bookshelf.models.book import Book, Genre
        
        # Check if book already exists by ISBN or title+author
        existing_book = None
        if book_data.get("isbn"):
            existing_book = Book.query.filter_by(isbn=book_data["isbn"]).first()
        
        if not existing_book:
            existing_book = Book.query.filter_by(
                title=book_data["title"], 
                author=book_data["author"]
            ).first()
        
        if existing_book:
            return existing_book
        
        # Create a new book
        new_book = Book(
            title=book_data["title"],
            author=book_data["author"],
            isbn=book_data.get("isbn", ""),
            description=book_data.get("description", ""),
            cover_url=book_data.get("cover_url", ""),
            publisher=book_data.get("publisher", ""),
            language=book_data.get("language", ""),
            page_count=book_data.get("page_count")
        )
        
        # Handle published date
        if book_data.get("published_date"):
            try:
                # If only a year is provided
                if isinstance(book_data["published_date"], int):
                    new_book.published_date = datetime(book_data["published_date"], 1, 1).date()
                else:
                    # Try to parse the date string
                    new_book.published_date = datetime.strptime(book_data["published_date"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        
        # Add genres
        if book_data.get("genres"):
            for genre_name in book_data["genres"]:
                # Limit genre name length
                genre_name = genre_name[:50] if len(genre_name) > 50 else genre_name
                
                # Check if genre exists or create a new one
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                
                new_book.genres.append(genre)
        
        db.session.add(new_book)
        db.session.commit()
        
        return new_book

    @staticmethod
    def import_books(query, limit=20):
        """
        Search for books and import them into the database
        
        Args:
            query (str): Search query
            limit (int): Maximum number of books to import
            
        Returns:
            list: List of imported book objects
        """
        books = OpenLibraryAPI.search_books(query, limit)
        imported_books = []
        
        for book_data in books:
            # Get additional details for books with IDs
            if book_data.get("open_library_id"):
                details = OpenLibraryAPI.get_book_details(book_data["open_library_id"])
                if details:
                    book_data.update(details)
            
            book = OpenLibraryAPI.save_book_to_db(book_data)
            imported_books.append(book)
        
        return imported_books 
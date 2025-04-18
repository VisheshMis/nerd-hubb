from datetime import datetime
from bookshelf.app import db

class BookFile(db.Model):
    """Model for storing uploaded book files"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_type = db.Column(db.String(50), nullable=False)  # e.g., 'application/pdf'
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)  # Optional link to a book
    
    def __repr__(self):
        return f'<BookFile {self.original_filename} ({self.file_type})>'
    
    @property
    def formatted_size(self):
        """Return human-readable file size"""
        size = self.file_size
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024 or unit == 'GB':
                return f"{size:.1f} {unit}"
            size /= 1024 
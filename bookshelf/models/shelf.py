from bookshelf.app import db
from datetime import datetime

class Shelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    status = db.Column(db.Enum('want_to_read', 'reading', 'read', name='shelf_status'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_started = db.Column(db.DateTime)
    date_finished = db.Column(db.DateTime)
    
    # Ensure a book can only be on one shelf per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
    )
    
    def __repr__(self):
        return f'<Shelf: {self.user_id} has {self.book_id} as {self.status}>' 
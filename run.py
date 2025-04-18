from bookshelf.app import create_app, db
from bookshelf.models import User, Book, Genre, Shelf, Review, Comment

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Book': Book, 
        'Genre': Genre, 
        'Shelf': Shelf,
        'Review': Review,
        'Comment': Comment
    }

if __name__ == '__main__':
    app.run(debug=True) 
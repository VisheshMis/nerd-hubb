# BookShelf

BookShelf is a social platform for book lovers to track reading, write reviews, rate books, and connect with others. Users can manage their reading lists (e.g., "Want to Read," "Currently Reading," "Read"), discover books, and engage with a community.

## Features

- **User Accounts**: Registration, login, user profiles with bio and stats
- **Book Management**: Search and browse books, add to shelves, rate and review
- **Social Features**: Follow users, activity feed, comment on reviews
- **Book Discovery**: Recommendations and trending books

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/bookshelf.git
cd bookshelf
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up environment variables (create a `.env` file in the project root):
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bookshelf.db  # or your PostgreSQL connection string
FLASK_APP=run.py
FLASK_ENV=development
```

5. Initialize the database:
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run the application:
```
python run.py
```

7. Access the application at `http://localhost:5000`

## Development

### Database Migrations

After modifying models, run:
```
flask db migrate -m "Description of changes"
flask db upgrade
```

### Running Tests

```
python -m unittest discover
```

## Deployment

For production deployment:

1. Set proper environment variables
2. Use a production WSGI server like Gunicorn
3. Set up with Nginx or another reverse proxy
4. Configure PostgreSQL database

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
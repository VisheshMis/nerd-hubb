import click
from flask.cli import with_appcontext
from bookshelf.utils.open_library import OpenLibraryAPI

@click.command("import-books")
@click.argument("query")
@click.option("--limit", default=20, help="Maximum number of books to import")
@with_appcontext
def import_books_command(query, limit):
    """Import books from Open Library API using a search query."""
    click.echo(f"Importing books matching '{query}'...")
    
    books = OpenLibraryAPI.import_books(query, limit)
    
    if books:
        click.echo(f"Successfully imported {len(books)} books:")
        for i, book in enumerate(books, 1):
            click.echo(f"{i}. {book.title} by {book.author}")
    else:
        click.echo("No books were imported.")
        
    return books

def register_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(import_books_command) 
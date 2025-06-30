import click
from flask.cli import with_appcontext
from app import db

@click.command('init-db')
@with_appcontext
def init_db():
    """Initialize the database with all tables."""
    try:
        click.echo('Initializing the database...')
        db.create_all()
        click.echo('Database initialized successfully!')
    except Exception as e:
        click.echo(f'Error initializing database: {str(e)}', err=True)
        raise

@click.command('drop-db')
@with_appcontext
def drop_db():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables?', abort=True):
        try:
            click.echo('Dropping all tables...')
            db.drop_all()
            click.echo('All tables dropped successfully!')
        except Exception as e:
            click.echo(f'Error dropping tables: {str(e)}', err=True)
            raise

@click.command('recreate-db')
@with_appcontext
def recreate_db():
    """Recreate database tables."""
    try:
        click.echo('Dropping all tables...')
        db.drop_all()
        click.echo('Creating all tables...')
        db.create_all()
        click.echo('Database recreated successfully!')
    except Exception as e:
        click.echo(f'Error recreating database: {str(e)}', err=True)
        raise

def register_commands(app):
    """Register CLI commands"""
    app.cli.add_command(init_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(recreate_db)

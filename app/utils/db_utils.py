import os
from app import db
from sqlalchemy import text

def execute_sql_file(filepath):
    """Execute a SQL file with proper text handling"""
    try:
        with open(filepath, 'r') as sql_file:
            sql_commands = sql_file.read()
            # Execute each statement separately
            for command in sql_commands.split(';'):
                if command.strip():
                    db.session.execute(text(command))
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error executing SQL file: {str(e)}")
        raise e

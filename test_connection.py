#!/usr/bin/env python3
"""
Test script to verify SQL Server connection
"""
import pyodbc
import sqlalchemy
from sqlalchemy import text
import time

def test_pyodbc_connection():
    """Test direct pyodbc connection"""
    print("Testing direct pyodbc connection...")
    
    conn_str = "mssql+pyodbc://sa:P@ssw0rd@host.docker.internal:1433/Speed?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        print(f"✅ PyODBC connection successful!")
        print(f"SQL Server version: {version[0]}")
        
        # Test database connection
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()
        print(f"Connected to database: {db_name[0]}")
        
        # Test if we can query tables
        cursor.execute("SELECT TOP 5 name FROM sys.tables")
        tables = cursor.fetchall()
        print(f"Available tables: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PyODBC connection failed: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\nTesting SQLAlchemy connection...")
    
    connection_string = "mssql+pyodbc://sa:P@ssw0rd@host.docker.internal:1433/Speed?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    
    try:
        engine = sqlalchemy.create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()
            print(f"✅ SQLAlchemy connection successful!")
            print(f"SQL Server version: {version[0]}")
            
            # Test database name
            result = conn.execute(text("SELECT DB_NAME()"))
            db_name = result.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
            # Test table query
            result = conn.execute(text("SELECT TOP 5 name FROM sys.tables"))
            tables = result.fetchall()
            print(f"Available tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {str(e)}")
        return False

def test_connection_with_retry(max_attempts=3, delay=2):
    """Test connection with retry logic"""
    print(f"Testing connection with {max_attempts} attempts...")
    
    for attempt in range(max_attempts):
        print(f"\n--- Attempt {attempt + 1}/{max_attempts} ---")
        
        pyodbc_success = test_pyodbc_connection()
        sqlalchemy_success = test_sqlalchemy_connection()
        
        if pyodbc_success and sqlalchemy_success:
            print("\n🎉 All connection tests passed!")
            return True
        elif attempt < max_attempts - 1:
            print(f"\n⏳ Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    print("\n❌ Connection tests failed after all attempts")
    return False

if __name__ == "__main__":
    print("=== SQL Server Connection Test ===")
    print("Connection string: mssql+pyodbc://sa:P@ssw0rd@172.20.192.1:1433/Speed?driver=ODBC+Driver+17+for+SQL+Server")
    print("=" * 50)
    
    success = test_connection_with_retry()
    
    if success:
        print("\n✅ Connection test completed successfully!")
        print("Your Flask app should be able to connect to this database.")
    else:
        print("\n❌ Connection test failed!")
        print("Please check:")
        print("1. SQL Server is running on 172.20.192.1:1433")
        print("2. Username 'sa' and password 'P@ssw0rd' are correct")
        print("3. Database 'Speed' exists")
        print("4. Firewall allows connections to port 1433")
        print("5. SQL Server is configured to accept remote connections") 
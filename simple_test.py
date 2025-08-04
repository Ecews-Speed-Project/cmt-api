#!/usr/bin/env python3
"""
Simple SQL Server connection test
"""
import pyodbc
import time

def test_connection():
    print("Testing connection to: 172.20.192.1:1433")
    print("Database: Speed")
    print("Username: sa")
    print("=" * 50)
    
    # Try different connection strings
    connection_strings = [
        # Standard connection string
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.20.192.1;DATABASE=Speed;UID=sa;PWD=P@ssw0rd;TrustServerCertificate=yes;",
        
        # With port specification
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.20.192.1,1433;DATABASE=Speed;UID=sa;PWD=P@ssw0rd;TrustServerCertificate=yes;",
        
        # With timeout
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=172.20.192.1;DATABASE=Speed;UID=sa;PWD=P@ssw0rd;TrustServerCertificate=yes;Connection Timeout=30;",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n--- Test {i} ---")
        print(f"Connection string: {conn_str}")
        
        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"✅ SUCCESS! SQL Server version: {version[0]}")
            
            # Test database name
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()
            print(f"Connected to database: {db_name[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Connection test successful!")
    else:
        print("\n❌ All connection attempts failed!")
        print("\nTroubleshooting tips:")
        print("1. Check if SQL Server is running on 172.20.192.1:1433")
        print("2. Verify username 'sa' and password 'P@ssw0rd'")
        print("3. Check if database 'Speed' exists")
        print("4. Verify firewall allows connections to port 1433")
        print("5. Check if SQL Server accepts remote connections") 
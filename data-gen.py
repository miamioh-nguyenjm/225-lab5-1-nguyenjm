import sqlite3
import os

DATABASE = '/nfs/demo.db'

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE)

def generate_test_data(num_contacts):
    db = connect_db()
    for i in range(num_contacts):
        name = f'Test Name {i}'
        phone = f'123-456-789{i}'
        email = f'test{i}@example.com'
        city = f'City{i}'
        country = 'Testland'
        username = f'testuser{i}'
        db.execute('''
            INSERT INTO contacts (name, phone, email, city, country, username)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, city, country, username))
    db.commit()
    print(f'{num_contacts} test contacts added to the database.')
    db.close()

if __name__ == '__main__':
    generate_test_data(10)  # Generate 10 test contacts.

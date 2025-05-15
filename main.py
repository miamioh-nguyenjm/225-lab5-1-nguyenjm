from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os
import requests

app = Flask(__name__)

# Path for the existing demo.db
DATABASE = '/nfs/demo.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Enable dictionary-style access
    return db

def init_db():
    with app.app_context():
        db = get_db()
        # Update the schema to include additional details:
        db.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                city TEXT,
                country TEXT,
                username TEXT
            );
        ''')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    # Handle manual entry submissions and deletion requests
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            contact_id = request.form.get('contact_id')
            db = get_db()
            db.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
            db.commit()
            message = 'Contact deleted successfully.'
        else:
            name = request.form.get('name')
            phone = request.form.get('phone')
            # For manual entry, additional fields remain empty
            if name and phone:
                db = get_db()
                db.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
                db.commit()
                message = 'Contact added successfully.'
            else:
                message = 'Missing name or phone number.'
    # Allow message (e.g. success message after generating a random person) to be passed as query parameter
    if not message:
        message = request.args.get('message', '')
    
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts').fetchall()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nguyen Lab 5-1</title>
        </head>
        <body>
            <h2>Nguyen Lab 5-1</h2>
            <form method="POST" action="/">
                <label for="name">Name:</label><br>
                <input type="text" id="name" name="name" required><br>
                <label for="phone">Phone Number:</label><br>
                <input type="text" id="phone" name="phone" required><br><br>
                <input type="submit" value="Submit Manual Entry">
            </form>
            <p>{{ message }}</p>
            {% if contacts %}
                <table border="1">
                    <tr>
                        <th>Name</th>
                        <th>Phone Number</th>
                        <th>Email</th>
                        <th>City</th>
                        <th>Country</th>
                        <th>Username</th>
                        <th>Delete</th>
                    </tr>
                    {% for contact in contacts %}
                        <tr>
                            <td>{{ contact['name'] }}</td>
                            <td>{{ contact['phone'] }}</td>
                            <td>{{ contact['email'] or '' }}</td>
                            <td>{{ contact['city'] or '' }}</td>
                            <td>{{ contact['country'] or '' }}</td>
                            <td>{{ contact['username'] or '' }}</td>
                            <td>
                                <form method="POST" action="/">
                                    <input type="hidden" name="contact_id" value="{{ contact['id'] }}">
                                    <input type="hidden" name="action" value="delete">
                                    <input type="submit" value="Delete">
                                </form>
                            </td>
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>No contacts found.</p>
            {% endif %}
            <br>
            <!-- New button to generate a random person -->
            <a href="{{ url_for('generate_random_person') }}">
                <button type="button">Generate Random Person</button>
            </a>
        </body>
        </html>
    ''', message=message, contacts=contacts)

@app.route('/generate', methods=['GET'])
def generate_random_person():
    # Call randomuser.me API to get a random fake person
    response = requests.get("https://randomuser.me/api/")
    if response.status_code == 200:
        data = response.json()
        user = data["results"][0]
        # Extract details from the API response
        first_name = user["name"]["first"]
        last_name = user["name"]["last"]
        name = f"{first_name} {last_name}"
        phone = user.get("phone", "N/A")
        email = user.get("email", "N/A")
        city = user["location"].get("city", "N/A")
        country = user["location"].get("country", "N/A")
        username = user["login"].get("username", "N/A")
        # Insert the randomly generated person into demo.db
        db = get_db()
        db.execute('INSERT INTO contacts (name, phone, email, city, country, username) VALUES (?, ?, ?, ?, ?, ?)',
                   (name, phone, email, city, country, username))
        db.commit()
        message = f"Random person ({name}) added successfully!"
    else:
        message = "Failed to retrieve random person data."
    return redirect(url_for('index', message=message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()  # Initialize the contacts table with the new schema
    app.run(debug=True, host='0.0.0.0', port=port)

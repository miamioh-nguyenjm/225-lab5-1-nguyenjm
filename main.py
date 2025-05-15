from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os
import requests  # newly imported to call the random user API

app = Flask(__name__)
app.secret_key = 'this-should-be-secret'  # Replace with a secure production key

# Database file path (demo.db remains your contacts database)
DATABASE = '/nfs/demo.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Enable access to columns by name
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            );
        ''')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    # Handle form submission for manual entries
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
            if name and phone:
                db = get_db()
                db.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
                db.commit()
                message = 'Contact added successfully.'
            else:
                message = 'Missing name or phone number.'
    # Check if a message was passed as a query parameter (used after generating a random person)
    if not message:
        message = request.args.get('message', '')
    
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts').fetchall()
    # The page now includes a new button that points to the '/generate' route.
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
                        <th>Delete</th>
                    </tr>
                    {% for contact in contacts %}
                        <tr>
                            <td>{{ contact['name'] }}</td>
                            <td>{{ contact['phone'] }}</td>
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
            <!-- New button: Clicking this calls the new API to generate a random person -->
            <a href="{{ url_for('generate_random_person') }}">
                <button type="button">Generate Random Person</button>
            </a>
        </body>
        </html>
    ''', message=message, contacts=contacts)

@app.route('/generate', methods=['GET'])
def generate_random_person():
    # Call the randomuser.me API to get a random fake person
    response = requests.get("https://randomuser.me/api/")
    if response.status_code == 200:
        data = response.json()
        user = data["results"][0]
        # Construct full name from first and last
        first_name = user["name"]["first"]
        last_name = user["name"]["last"]
        name = f"{first_name} {last_name}"
        # Use the 'phone' field from the API response (or default to N/A)
        phone = user.get("phone", "N/A")
        # Insert the generated random person into the contacts table
        db = get_db()
        db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
        db.commit()
        message = f"Random person ({name}) added successfully!"
    else:
        message = "Failed to retrieve random person data."
    # Redirect back to index with a message
    return redirect(url_for('index', message=message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()  # Initialize the contacts table in demo.db
    app.run(debug=True, host='0.0.0.0', port=port)

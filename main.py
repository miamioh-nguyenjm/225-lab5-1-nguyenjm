from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)

DATABASE = '/nfs/demo.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Use name-based access to columns
    return db

def init_db():
    with app.app_context():
        db = get_db()
        # Create a table for entries if it doesn't already exist.
        db.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            );
        ''')
        db.commit()

@app.route('/')
def index():
    db = get_db()
    entries = db.execute('SELECT * FROM entries').fetchall()
    return render_template('index.html', entries=entries)

@app.route('/play', methods=['GET'])
def play():
    # Display the simple text-based game (a number guessing challenge)
    return render_template('play.html')

@app.route('/guess', methods=['POST'])
def guess():
    try:
        guess = int(request.form.get('guess'))
    except (ValueError, TypeError):
        return render_template('play.html', message="Please enter a valid number!")
    
    secret = 2  # For example, the secret number is fixed at 2
    if guess == secret:
        session['game_passed'] = True
        return redirect(url_for('add_entry'))
    else:
        return render_template('play.html', message="Wrong guess. Try again!")

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if not session.get('game_passed'):
        # If the game hasn't been won, redirect to the game page.
        return redirect(url_for('play'))
    
    message = ""
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            db = get_db()
            db.execute('INSERT INTO entries (content) VALUES (?)', (content,))
            db.commit()
            message = "Entry added successfully!"
            # Reset the game flag so that the next entry requires playing again.
            session['game_passed'] = False
        else:
            message = "Please enter some content for your entry."
    return render_template('add_entry.html', message=message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()  # Initialize the database and table
    app.run(debug=True, host='0.0.0.0', port=port)

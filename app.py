from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Keep things simple: read secret from env with a fallback for development
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')  # set SECRET_KEY in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Task model (simple, no created_at to avoid schema mismatch)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Define the Contact model (no created_at column for simplicity)
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def index():
    # Simple, reliable ordering by id (latest first). Avoids schema-dependent columns.
    tasks = Task.query.order_by(Task.id.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title:
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:id>')
def toggle_task(id):
    task = Task.query.get(id)
    if task:
        task.completed = not task.completed
        db.session.commit()
        status = 'completed' if task.completed else 'uncompleted'
        flash(f'Task marked as {status}!', 'success')
    return redirect(url_for('index'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if name and email and message:
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        flash('Thank you for your message! We will get back to you soon.', 'success')
    else:
        flash('Please fill in all fields.', 'error')
    
    return redirect(url_for('contact'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
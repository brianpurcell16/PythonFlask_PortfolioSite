import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key')

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash(
    os.environ.get('ADMIN_PASSWORD', 'fallback-dev-password')
)

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USERNAME:
        return User(user_id)
    return None

# --- Database helpers ---

def get_db_connection():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.autocommit = False
    return conn

def get_project(project_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM projects WHERE id = %s', (project_id,))
    project = cur.fetchone()
    cur.close()
    conn.close()
    if project is None:
        abort(404)
    return project

# --- Create tables if they don't exist ---

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id          SERIAL PRIMARY KEY,
            created     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            title       TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack  TEXT,
            github_url  TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- Public routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM projects ORDER BY created DESC')
    all_projects = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/<int:project_id>')
def project(project_id):
    p = get_project(project_id)
    return render_template('project.html', project=p)

@app.route('/about')
def about():
    return render_template('about.html')

# --- Login / Logout ---

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            login_user(User(username))
            return redirect(url_for('projects'))
        else:
            flash('Incorrect username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

# --- Protected routes ---

@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title       = request.form['title']
        description = request.form['description']
        tech_stack  = request.form['tech_stack']
        github_url  = request.form['github_url']

        if not title:
            flash('Project title is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO projects (title, description, tech_stack, github_url) VALUES (%s, %s, %s, %s)',
                (title, description, tech_stack, github_url)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('projects'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    p = get_project(id)

    if request.method == 'POST':
        title       = request.form['title']
        description = request.form['description']
        tech_stack  = request.form['tech_stack']
        github_url  = request.form['github_url']

        if not title:
            flash('Project title is required!')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'UPDATE projects SET title=%s, description=%s, tech_stack=%s, github_url=%s WHERE id=%s',
                (title, description, tech_stack, github_url, id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('projects'))

    return render_template('edit.html', project=p)

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    p = get_project(id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM projects WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('"{}" was deleted.'.format(p['title']))
    return redirect(url_for('projects'))
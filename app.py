import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flaskportfolioprojectpython'

# Flask login setup 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #gets redirected if not logged in


# Hardcodding an admin user in
class User(UserMixin):
    def __init__(self,id):
        self.id = id

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin')

@login_manager.user_loader
def load_user(user_id):
    if user_id == ADMIN_USERNAME:
        return User(user_id)
    return None

#Helper commands for the database

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row #allows columns to be acessed by names
    return conn

def get_project(project_id):
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?',(project_id,)).fetchone()
    conn.close()
    if project is None:
        abort(404)
    return project

#Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    conn = get_db_connection()
    all_projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/<int:project_id>')
def project(project_id):
    selectedProject = get_project(project_id)
    return render_template('project.html', project=selectedProject)

@app.route('/about')
def about():
    return render_template('about.html')

#Routes for login and logout

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            login_user(User(username))
            return redirect(url_for('projects'))
        else:
            flash('Incorrect username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))


#These routes are protected meaning the user must be logged in
@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        tech_stack = request.form['tech_stack']
        url = request.form['github_url']

        if not title:
            flash('A title is needed for this project!')
        elif not url:
            flash('A url to GitHub is needed!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO projects (title, description, tech_stack, github_url) VALUES (?, ?, ?, ?)',
                         (title, desc, tech_stack, url)
                         )
            conn.commit()
            conn.close()
            return redirect(url_for('projects'))
        
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    selectedProject = get_project(id)

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        tech_stack = request.form['tech_stack']
        url = request.form['github_url']

        if not title:
            flash('A title is needed for this project!')
        elif not url:
            flash('A url to GitHub is needed!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE projects SET title=?, description=?, tech_stack=?, github_url=? WHERE id=?',
                        (title, desc, tech_stack, url, id)
                         )
            conn.commit()
            conn.close()
            return redirect(url_for('projects'))
        
    return render_template('edit.html', project=selectedProject)


@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    selectedProject = get_project(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was deleted.'.format(selectedProject['title']))
    return redirect(url_for('projects'))


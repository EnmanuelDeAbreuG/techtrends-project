import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connection_count = 0


def get_db_connection():
    """Create a DB connection and increment the connection counter.

    Note: This uses a module-level counter which works for this single-process
    exercise. In production, with multiple processes/replicas, a different
    approach would be needed.
    """
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.testing = True  # Enable testing mode for test_client


# Configure logging to output to STDOUT and include timestamps
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s: %(message)s',
                              datefmt='%m/%d/%Y, %H:%M:%S')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

root = logging.getLogger()
root.setLevel(logging.DEBUG)
if not root.handlers:
    root.addHandler(handler)
else:
    # ensure our handler is present
    root.handlers = [handler]

# ensure werkzeug logs are visible (requests)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
            app.logger.info('Article with id %s not found.', post_id)
            return render_template('404.html'), 404
    else:
            app.logger.info('Article "%s" retrieved!', post['title'])
            return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info('Article "%s" created!', title)
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthz():
    """Health check endpoint. Returns simple JSON + 200."""
    return jsonify({'result': 'OK - healthy'}), 200


@app.route('/metrics')
def metrics():
    """Metrics endpoint returning DB connection count and post count."""
    try:
        connection = get_db_connection()
        post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
        connection.close()
    except Exception:
        # If there's any error (e.g. DB/table doesn't exist), return zeros.
        post_count = 0

    return jsonify({
        'db_connection_count': db_connection_count,
        'post_count': post_count
    }), 200

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')

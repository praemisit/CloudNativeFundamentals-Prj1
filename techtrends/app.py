import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging, sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connections_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    
    # We shall count the total number of connections to the dabase
    db_connections_count += 1
    
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
logger = logging.getLogger(__name__)

# Reset db connection counter to 0 
db_connections_count = 0


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
      logger.info("A non existing article was accessed")  
      return render_template('404.html'), 404
    else:
      messagetext = "Article \"" + post['title'] + "\" has been retrieved successfully."
      logger.info(messagetext)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About us request successfull')
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
            messagetext = "A new article \"" + title + "\" has been created successfully."
            logger.info(messagetext)
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response


@app.route('/metrics')
def metrics():
    m_dict = {}
    connection = get_db_connection()
    m_dict["post_count"] = connection.execute('SELECT count(*) FROM posts').fetchone()[0]
    m_dict["db_connection_count"] = db_connections_count
    connection.close()
    response = app.response_class(
            response=json.dumps({"Status":"OK", "data": m_dict}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.handlers = []
    # Set the lowest-severity log message to DEBUG
    logger.setLevel(10)
    
    # Create and config handlers
    sout_handler = logging.StreamHandler(sys.stdout)
    serr_handler = logging.StreamHandler(sys.stderr)
    sout_handler.setLevel(logging.DEBUG)
    serr_handler.setLevel(logging.DEBUG)

    sout_format = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
    serr_handler.setFormatter(sout_format)
    sout_handler.setFormatter(sout_format)

    logger.addHandler(sout_handler)
    logger.addHandler(serr_handler)

    app.run(host='0.0.0.0', port='3111')

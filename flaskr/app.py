import os

from flask import Flask


"""Create and configure an instance of the Flask application."""
app = Flask(__name__, instance_relative_config=True,static_url_path='/static')
app.config.from_mapping(
    # a default secret that should be overridden by instance config
    SECRET_KEY="dev",
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
)
UPLOAD_FOLDER = './static/upload/'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# register the database commands
from flaskr import db
db.init_app(app)

# apply the blueprints to the app
from flaskr import auth, blog

app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)


# make url_for('index') == url_for('blog.index')
# in another app, you might define a separate main index here with
# app.route, while giving the blog blueprint a url_prefix, but for
# the tutorial the blog will be the main index
app.add_url_rule("/", endpoint="index")




if __name__ == '__main__':
    app.run(debug=True) 
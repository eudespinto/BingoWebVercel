import os
from flask import Flask
import platform
from flask_mysqldb import MySQL
from dotenv import load_dotenv
# from .utils.momentjs import *

load_dotenv()


def create_app(test_config=None):
    # create and configure the app
    # app = Flask(__name__, instance_relative_config=True)
    app = Flask(__name__)
    # if platform.system() == 'Windows':
    #     app = Flask(__name__, instance_path=os.path.abspath('.\\instance'))
    # else:
    #     app = Flask(__name__, instance_path=os.path.abspath('./instance'))
    # app.jinja_env.globals['momentjs'] = momentjs
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        MYSQL_HOST=os.getenv('MYSQL_HOST'),
        MYSQL_PORT=os.getenv('MYSQL_PORT'),
        MYSQL_USER=os.getenv('MYSQL_USER'),
        MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD'),
        # MYSQL_DB=os.getenv('MYSQL_DB'),
        MYSQL_DB='bingo',
        # MYSQL_NAME='bingo',
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # inicializar MySQL
    mysql = MySQL(app)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # from . import blog
    # app.register_blueprint(blog.bp)

    from . import bingo
    app.register_blueprint(bingo.bp)
    app.add_url_rule('/', endpoint='index')

    return app.run()

# export FLASK_APP=flaskr
# export FLASK_ENV=development
# flask --app flaskr init-db
# flask --app flaskr --debug run -p 8900


if __name__ == '__main__':
    create_app()

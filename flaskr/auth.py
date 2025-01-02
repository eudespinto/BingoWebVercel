import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import execute_commit, execute_fetchone
from mysql.connector import IntegrityError

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                sql = "INSERT INTO `user` (username, password) VALUES (%s, %s)"
                parameters = (username, generate_password_hash(password))
                execute_commit(sql=sql, parameters=parameters)
            except IntegrityError:
                error = f"User {username} is already registered."
            except Exception as e:
                error = str(e)
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = None
        try:
            sql = 'SELECT * FROM `user` WHERE username = %s'
            parameters = (username,)
            user = execute_fetchone(sql=sql, parameters=parameters,
                                    dictionary=True)
            print(user)

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'
        except Exception as e:
            print(e)

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        sql = 'SELECT * FROM `user` WHERE id = %s'
        parameters = (user_id,)
        g.user = execute_fetchone(sql=sql, parameters=parameters,
                                  dictionary=True)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

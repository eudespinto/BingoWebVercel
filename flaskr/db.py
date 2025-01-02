# import sqlite3
# import MySQLdb
import mysql.connector as mysqldb
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db(cursor=False):
    if 'db' not in g:
        # g.db = sqlite3.connect(
        #     current_app.config['DATABASE'],
        #     detect_types=sqlite3.PARSE_DECLTYPES
        # )
        # g.db.row_factory = sqlite3.Row
        g.db = mysqldb.connect(
            host=current_app.config['MYSQL_HOST'],
            port=int(current_app.config['MYSQL_PORT']),
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
    if cursor:
        return g.db.cursor()
    return g.db


def execute_commit(sql, parameters=None, dictionary=False):
    db = get_db()
    if dictionary:
        cursor = db.cursor(dictionary=True)
    else:
        cursor = db.cursor()
    if parameters is not None:
        cursor.execute(sql, tuple(parameters))
    else:
        cursor.execute(sql)
    db.commit()
    cursor.close()


def execute_fetchone(sql, parameters=None, dictionary=False):
    db = get_db()
    if dictionary:
        cursor = db.cursor(dictionary=True)
    else:
        cursor = db.cursor()
    if parameters is not None:
        cursor.execute(sql, tuple(parameters))
    else:
        cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    return result


def execute_fetchall(sql, parameters=None, dictionary=True):
    db = get_db()
    if dictionary:
        cursor = db.cursor(dictionary=True)
    else:
        cursor = db.cursor()
    if parameters is not None:
        cursor.execute(sql, tuple(parameters))
    else:
        cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        # db.executescript(f.read().decode('utf8'))
        sql = f.read().decode('utf8')
        cursor = db.cursor()
        for command in sql.split(';'):
            command = command.strip()
            if command:  # Certifique-se de que o comando não está vazio
                try:
                    cursor.execute(command)
                    db.commit()
                except mysqldb.Error as err:
                    # Exibir mensagem de erro caso algum comando falhe
                    print(f"Erro ao executar comando: {command}\n{err}")
                    db.rollback()  # Caso ocorra erro, faça rollback da transação atual
                    break  # Se necessário, pode interromper a execução em caso de erro

        cursor.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

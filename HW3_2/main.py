import flask
from flask import Flask, render_template, request, redirect, url_for, make_response
import hashlib
import sqlite3
import pdfkit
from os import path

app = Flask(__name__, static_folder='src+data', static_url_path='/')
app.current_user = "~#NAN#~"


@app.route('/')
def authorization_page():
    return render_template('authorization_page.html', error_value="")


@app.route('/resume')
def main_page():
    if app.current_user == "~#NAN#~":
        return redirect(url_for('login'))
    else:
        db_connection = sqlite3.connect('DATABASE.db')
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM draft WHERE username = '" + app.current_user + "'")
        req = cursor.fetchall()
        if len(req) == 0:
            return render_template('main_page.html',
                                   first_name="",
                                   last_name="",
                                   _date_born_="",
                                   description="")
        else:
            return render_template('main_page.html',
                                   first_name=req[0][1],
                                   last_name=req[0][2],
                                   _date_born_=str(req[0][3]),
                                   description=req[0][4])


@app.route('/', methods=['post', 'get'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    hash_object = hashlib.sha256(password.encode())
    hex_dig = hash_object.hexdigest()
    if login_try(username, hex_dig):
        app.current_user = username
        return redirect(url_for('main_page'))
    else:
        return render_template('authorization_page.html', error_value="Wrong login or password")


@app.route('/registration/', methods=['get'])
def registration():
    return render_template('registration_page.html', error_value="")


@app.route('/registration/', methods=['post', 'get'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
    if ',' in username:
        return render_template('registration_page.html', error_value="В логине есть недопустимые символы")
    elif len(username) < 4 or len(username) > 16:
        return render_template('registration_page.html', error_value="Логин должен быть от 4 до 16 символов")
    elif password != repeat_password:
        return render_template('registration_page.html', error_value="Разные пароли")
    elif len(password) < 8 or len(password) > 16:
        return render_template('registration_page.html', error_value="Пароль должен быть от 8 до 16 символов")
    else:
        hash_object = hashlib.sha256(password.encode())
        hex_dig = hash_object.hexdigest()
        if register_try(username, hex_dig):
            return redirect(url_for('authorization_page'))
        else:
            return render_template('registration_page.html', error_value="Пользователь с таким логином уже существует")


def login_try(username, hash_password):
    db_connection = sqlite3.connect('DATABASE.db')
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users_data WHERE username = '" + username + "'")
    req = cursor.fetchall()
    if len(req) == 0:
        db_connection.close()
        return 0
    else:
        if req[0][1] == hash_password:
            db_connection.close()
            return 1
        else:
            db_connection.close()
            return 0


def register_try(username, hash_password):
    db_connection = sqlite3.connect('DATABASE.db')
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users_data WHERE username = '" + username + "'")
    req = cursor.fetchall()
    if len(req) != 0:
        db_connection.close()
        return 0
    else:
        cursor.execute("INSERT INTO users_data VALUES ('" + username + "', '" + hash_password + "')")
        db_connection.commit()
        db_connection.close()
        return 1


@app.route('/resume/', methods=['post', 'get'])
def save_resume():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date = request.form.get('date')
        description = request.form.get('description')
    db_connection = sqlite3.connect('DATABASE.db')
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM draft WHERE username = '" + app.current_user + "'")
    req = cursor.fetchall()
    if len(req) == 0:
        cursor.execute("INSERT INTO draft VALUES ('" + app.current_user + "', '"
                       + first_name + "', '"
                       + last_name + "', '"
                       + date + "', '"
                       + description + "')")
    else:
        sqlite_update_query = """UPDATE draft set first_name = ?,
                                    last_name = ?,
                                    date_born = ?,
                                    description = ?
                                    where username = ?"""
        column_values = (first_name, last_name, date, description, app.current_user)
        cursor.execute(sqlite_update_query, column_values)

    db_connection.commit()
    db_connection.close()
    return redirect(url_for('main_page'))


@app.route('/download/')
def download():
    if app.current_user == "~#NAN#~":
        return redirect(url_for('login'))
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
    scan = main_page()
    pdf = pdfkit.from_string(scan, False, configuration=config)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=resume.pdf"
    return response


if __name__ == '__main__':
    app.run()

import os
from flask import Flask, render_template, send_from_directory, redirect, make_response, request
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Email
import os.path

import models
from models import db

class LoginForm(FlaskForm):
    user_first_name = StringField('First Name', validators=[DataRequired()])
    user_last_name = StringField('Last Name', validators=[DataRequired()])
    user_email = StringField('Email', validators=[DataRequired(), Email()])
    user_password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('user_password', message='Пароли должны совпадать')
                                                ])


app = Flask(__name__)

# В консоли python:
# >>> import secrets
# >>> secrets.token_hex()
# Получим уникальный ключ

app.config['SECRET_KEY'] = 'd4d339aa6034973adf6714d6cf5c629c71c04425af7d9a1bfdc416c1790fd23c'
csrf = CSRFProtect(app)
db_filename = 'mydatabase.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_filename}'
db.init_app(app)

@app.route('/')
def index():
    return make_response(redirect('/login/'))

@app.route('/login/', methods=['GET', 'POST'])
@csrf.exempt
def login():
    form = LoginForm()
    print(f'{form.validate()}')
    if request.method == 'POST' and form.validate():
        context = {'login': {
            'user_first_name': form.user_first_name.data,
            'user_last_name': form.user_last_name.data,
            'user_email': form.user_email.data,
            'user_password': form.user_password.data,
        }}

        if not os.path.exists(db_filename):
            db.create_all()

        user = models.User(first_name = form.user_first_name.data,
                           last_name = form.user_last_name.data,
                           email = form.user_email.data,
                           password = form.user_password.data
                           )
        db.session.add(user)
        db.session.commit()
        response = make_response(render_template('confirm.html', **context))
        return response
    return render_template('index.html', form = form)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)



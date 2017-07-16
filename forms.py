from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import validators

from model import User

class SignupForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter a valid email address.")])
    password = PasswordField('Password',
                             [validators.Required("Please enter a password."),
                              validators.Length(min=8, max=64)])
    confirm = PasswordField('Confirm Password',
                            [validators.EqualTo('password', message='Passwords must match.')])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            email.errors.append('An account with that email address already exists.')
            return False
        return True

class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')

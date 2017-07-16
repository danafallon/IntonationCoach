from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import validators


class SignupForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter a valid email address.")])
    password = PasswordField('Password',
                             [validators.Required("Please enter a password."),
                              validators.Length(min=8, max=64)])
    confirm = PasswordField('Confirm Password',
                            [validators.EqualTo('password', message='Passwords must match.')])

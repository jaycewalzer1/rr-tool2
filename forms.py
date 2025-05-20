from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
import re

def validate_cognito_password(form, field):
    password = field.data
    # Check length
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(), Email()
    ])
    
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message="Phone number must be 10 digits")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long'),
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    
    submit = SubmitField('Sign Up')


class ConfirmForm(FlaskForm):
    confirmation_code = StringField('Confirmation Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Confirmation code must be 6 digits')
    ])
    submit = SubmitField('Confirm Account')

class ResetCodeForm(FlaskForm):
    confirmation_code = StringField('Confirmation Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Confirmation code must be 6 digits')
    ])
    submit = SubmitField('Confirm Reset')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Code')

class ConfirmResetForm(FlaskForm):
    confirmation_code = StringField('Confirmation Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Confirmation code must be 6 digits')
    ])
    submit = SubmitField('Verify Code')

class NewPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')
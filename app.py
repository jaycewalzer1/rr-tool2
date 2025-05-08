from flask import Flask, render_template, redirect, url_for, request, flash
from forms import LoginForm, SignupForm, ResetPasswordForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True
app.config['SERVER_NAME'] = None
app.config['ENV'] = 'development'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/marketing')
def marketing():
    return render_template('marketing.html')

@app.route('/dashboard/database')
def database():
    return render_template('database.html')

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/company')
def company():
    return render_template('404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        flash('Password reset link sent to your email.')
        return redirect(url_for('login'))
    return render_template('reset.html', form=form)

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route("/contact")
def contact():
    return render_template("404.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()

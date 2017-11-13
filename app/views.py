from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm
from flask_login import login_user, logout_user, current_user
from .oauth import OAuthSignIn

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Kevin'}
    posts = [
        {
            'author': {'nickname' : 'John'},
            'body' : 'Beautiful day in Idaho Falls!'
        },
        {
            'author': {'nickname' : 'Susan'},
            'body' : 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                            title='Home',
                            user=user,
                            posts=posts)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In')

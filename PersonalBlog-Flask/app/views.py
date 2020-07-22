from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm
from .models import User, Post
from .forms import LoginForm, EditForm, PostForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from config import POSTS_PER_PAGE

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page = 1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now released!')
        return redirect(url_for('index'))

    posts = []
    
    if g.user is None or not g.user.is_authenticated :
        users = User.query.all()
        for u in users:
            posts.append(u.followed_posts())
    else:
        posts = g.user.followed_posts()
    posts = posts.paginate(page, POSTS_PER_PAGE, False)#paginate对象，items属性才是list
    return render_template("index.html", title="Home",form=form, posts=posts)

#注册
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if g.user != None and g.user.is_authenticated :
        flash("Current user exist! Need not to sign in.")
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        if create_user(form):
            flash('Create User Succeed.')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Sign in failed,Name have been used! Please choose another one.')
    
    return render_template('sign_in.html', title = "Sign In", form=form) 

#创建用户，没有时便创建加登录
def create_user(user_form):
    if user_form.nickname is None or user_form.nickname.data == "":
        return False
    
    user = User.query.filter_by(nickname=user_form.nickname.data).first()
    if user is not None:
        return False
    nickname = User.make_unique_nickname(user_form.nickname.data)
    user = User(nickname=user_form.nickname.data, password=user_form.password.data,email=user_form.email.data)
    db.session.add(user)
    db.session.commit()
    db.session.add(user.follow(user))
    db.session.commit()

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember= remember_me)
    return True

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        flash('Current user exist! Do not login repetitious.')
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        if validate_user(form):
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash("User Info is invalid! Can not login.")

    return render_template('login.html', title = "Login", form=form)

#验证用户是否存在于数据库，不存在则提示进入注册页面
def validate_user(user_form):
    if user_form.nickname is None or user_form.nickname.data == "":
        return False
    
    user = User.query.filter_by(nickname=user_form.nickname.data).first()
    if user is None:
        return False
    if user.nickname != user_form.nickname.data or user.password != user_form.password.data:
        return False

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember= remember_me)
    return True

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html', user = user, posts = posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved!')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'),500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s is not found!' % nickname)
        return redirect(url_for('index'))
    
    if user == g.user:
        flash('You can not follow yourself! ')
        return redirect(url_for('user', nickname=nickname))

    u = g.user.follow(user)
    if u is None:
        flash('Can not follow ' + nickname + ".")
        return redirect(url_for('user',nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname +"!")
    return redirect(url_for('user', nickname=nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))
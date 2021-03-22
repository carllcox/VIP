from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, policyForm, RatePolicyForm1, RatePolicyForm2
from app.email import send_password_reset_email
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random
from starterdata.loaddatabase import create_location_table
from app.models import User, Location

@app.route('/',  methods=['GET', 'POST'])
@app.route('/index',  methods=['GET', 'POST'])
def index():

    return render_template('about.html', title='About')

@app.route('/api/v1.0/randomlocation')
def randomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : location.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/getrandomlocation', methods=['GET'])
def getrandomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : location.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/postrandomlocation', methods=['POST'])
def postrandomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : location.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/location/<id>', methods=['GET'])
def getlocation(id):
    location = Location.query.filter_by(id=id).first()

    return jsonify({ 'id' : location.id, 'lat' : location.location_lat, 'long' : location.location_long, 'name' : location.location_name })


@app.route('/FSLKfjkdlja832587fda',  methods=['GET', 'POST'])
def loaddata():
    print("start")
    create_location_table("starterdata/ParsedData.csv")
    print("done")

    return render_template('500.html', title='What are you doing here?')

@app.route('/about')
def about():

    return render_template('about.html', title='About')

@app.route('/data-analysis')
def data_analysis():

    return render_template('data_analysis.html', title='data-analysis')


@app.route('/admin')
@login_required
def admin():

    return render_template('admin.html', title='Admin Dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

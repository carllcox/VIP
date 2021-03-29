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
from app.models import User, Location, UserReport, CovidReports

@app.route('/',  methods=['GET', 'POST'])
@app.route('/index',  methods=['GET', 'POST'])
def index():

    return render_template('about.html', title='About')

@app.route('/api/v1.0/randomlocation')
def randomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : randomlocation.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/getrandomlocation', methods=['GET'])
def getrandomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : randomlocation.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/postrandomlocation', methods=['POST'])
def postrandomlocation():
    randomlocation = Location.query.order_by(func.random()).first()

    return jsonify({ 'id' : randomlocation.id, 'lat' : randomlocation.location_lat, 'long' : randomlocation.location_long, 'name' : randomlocation.location_name })

@app.route('/api/v1.0/location/<id>', methods=['GET'])
def getlocation(id):
    location = Location.query.filter_by(id=id).first()

    return jsonify({ 'id' : location.id, 'lat' : location.location_lat, 'long' : location.location_long, 'name' : location.location_name, 'mask_level' : location.current_mask_level, 'busyness_level' : location.current_busyness_level, 'computed_timestamp' : location.last_computed, 'average_mask_level' : location.average_mask_level, 'average_busyness_level' : location.average_busyness_level, 'policy_description' : location.policy_description })

@app.route('/api/v1.0/location/', methods=['GET'])
def getrequestlocation():
    location_id = request.form['location_id']

    location = Location.query.filter_by(id=location_id).first()

    return jsonify({ 'id' : location.id, 'lat' : location.location_lat, 'long' : location.location_long, 'name' : location.location_name, 'mask_level' : location.current_mask_level, 'busyness_level' : location.current_busyness_level, 'computed_timestamp' : location.last_computed, 'average_mask_level' : location.average_mask_level, 'average_busyness_level' : location.average_busyness_level, 'policy_description' : location.policy_description })

@app.route('/api/v1.0/location/<lat>/<long>', methods=['GET'])
def getlocationinlat(lat, long):

    lat = float(lat)
    long = float(long)

    location = Location.query.filter(Location.location_lat.between(lat - 0.0001, lat + 0.0001), Location.location_long.between(long - 0.0001, long + 0.0001)).order_by(func.random()).first()

    return jsonify({ 'id' : location.id, 'lat' : location.location_lat, 'long' : location.location_long, 'name' : location.location_name, 'mask_level' : location.current_mask_level, 'busyness_level' : location.current_busyness_level, 'computed_timestamp' : location.last_computed, 'average_mask_level' : location.average_mask_level, 'average_busyness_level' : location.average_busyness_level, 'policy_description' : location.policy_description })


@app.route('/api/v1.0/location_in_bounds/bounds', methods=['GET'])
def locations_in_bounds():
    lower_lat = request.args['lower_lat']
    upper_lat = request.args['upper_lat']
    lower_long = request.args['lower_long']
    upper_long = request.args['upper_long']

    locations = Location.query.filter(Location.location_lat.between(lower_lat, upper_lat), Location.location_long.between(lower_long, upper_long)).limit(100)

    ids = []
    lats = []
    longs = []
    names = []
    for location in locations:
        ids.append(location.id)
        lats.append(location.location_lat)
        longs.append(location.location_long)
        names.append(location.location_name)

    return jsonify({ 'ids' : ids, 'lats' : lats, 'longs' : longs, 'names' : names})

@app.route('/api/v1.0/search/<query_text>', methods=['GET'])
def searchlocations(query_text):
    locations = Location.query.filter(Location.location_name.ilike("%" + query_text + "%"))

    ids = []
    lats = []
    longs = []
    names = []
    for location in locations:
        ids.append(location.id)
        lats.append(location.location_lat)
        longs.append(location.location_long)
        names.append(location.location_name)

    return jsonify({ 'ids' : ids, 'lats' : lats, 'longs' : longs, 'names' : names})

@app.route('/api/v1.0/reviews/<location_id>', methods=['GET'])
def getreviews(location_id):
    reviews = UserReport.query.filter_by(location_id = location_id)

    ids = []
    ratings = []
    rating_comments = []
    for review in reviews:
        ids.append(review.id)
        ratings.append(review.review_rating)
        if review.review_comment_approved:
            rating_comments.append(review.review_comment)
        else:
            rating_comments.append(None)

    return jsonify({ 'location_id' : location_id, 'review_ids' : id, 'ratings' : ratings, 'rating_comments' : rating_comments})


@app.route('/api/v1.0/reviews/<location_id>', methods=['POST'])
def postreviews(location_id):
    # TODO: Add data validation

    location_id = request.form['location_id']
    mask_level = request.form['mask_level']
    busyness_level = request.form['busyness_level']

    policy_followed = request.form['policy_followed']
    policy_comment = request.form['policy_comment']

    review_rating = request.form['review_rating']
    review_comment = request.form['review_comment']

    if current_user.is_authenticated:
        new_report = UserReport(user_id=current_user.id, location_id=location_id, \
            mask_level=mask_level, busyness_level=busyness_level, \
            policy_followed=policy_followed, policy_comment=policy_comment, \
            review_rating=review_rating, review_comment=review_comment)
    else:
        new_report = UserReport(location_id = location_id, \
            mask_level=mask_level, busyness_level=busyness_level, \
            policy_followed=policy_followed, policy_comment=policy_comment, \
            review_rating=review_rating, review_comment=review_comment)

    db.session.add(new_report)
    db.session.commit()

    return jsonify({ 'Success' : True })

@app.route('/api/v1.0/postid/<post_id>', methods=['POST'])
def postid(post_id):
    report = CovidReports(id=post_id)
    db.session.add(report)
    db.session.commit()

    return jsonify({ 'Success' : True })

@app.route('/api/v1.0/checkpost/<post_id>')
def checkpost(post_id):
    report = CovidReports.query.filter_by(id=post_id).first();

    return jsonify({ "Success" : report != None });


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

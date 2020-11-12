from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User, Policy, Vote, PolicyVote
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm, policyForm, RatePolicyForm1, RatePolicyForm2

from app.email import send_password_reset_email
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import except_
import random

@app.route('/',  methods=['GET', 'POST'])
@app.route('/index',  methods=['GET', 'POST'])
def index():

    #There's an upvote error that needs to be fixed :(

    random_policy = Policy.query.order_by(func.random()).first()

    policyTitle, policyDescription, totalVotes = random_policy.title, random_policy.description, random_policy.total_votes

    form1 = RatePolicyForm1()
    form2 = RatePolicyForm2()

    if form1.submit1.data and form1.validate():

        if type(random_policy.total_votes) != int:
             random_policy.total_votes = 1
        else:
            random_policy.total_votes += 1

        user_policy_vote = Vote.query.filter_by(user_id=current_user.id, policy_id_1=random_policy.id).first()

        if user_policy_vote is not None:
            vote = Vote(user_id=current_user.id, policy_id_1=random_policy.id)
            db.session.add(vote)
            db.session.commit()
            db.session.refresh(vote)

            policyVote = PolicyVote(policy_id = random_policy.id, vote_id = vote.id)
            db.session.add(PolicyVote)
            db.session.commit()
        else:
            flash("You've already voted on this random policy :)")

        return redirect(url_for('index'))

    if form2.submit2.data and form2.validate():
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', form1 = form1, form2 = form2,
        policyTitle = policyTitle, policyDescription = policyDescription, totalVotes = totalVotes)

@app.route('/about')
def about():

    return render_template('about.html', title='About')

@app.route('/data-analysis')
def data_analysis():

    return render_template('data_analysis.html', title='data-analysis')

@app.route('/leaderboard')
def leaderboard():

    policies = Policy.query.limit(10).all()
    tripList = sorted([[policy.title, policy.description, policy.total_votes] for policy in policies if type(policy.total_votes) == int],
        key = lambda x: x[2], reverse = True)[:10]

    users = User.query.limit(10).all()
    tupList = sorted([(user.name, user.contributionPoints) for user in users if type(user.contributionPoints) == int],
    key = lambda x: x[1], reverse = True)[:10]

    return render_template('leaderboard.html', title='Leaderboard', tripList= tripList, tupList = tupList)

@app.route('/admin')
@login_required
def admin():

    return render_template('admin.html', title='Admin Dashboard')

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):

    user = User.query.filter_by(username=username).first_or_404()
    policies = Policy.query.filter_by(user_id=user.id)
    tupList = [(policy.title, policy.description) for policy in policies]

    form = policyForm()

    if form.validate_on_submit():

        policy = Policy(user_id = user.id , title = form.policy.data, description = form.description.data)

        if policy:
            db.session.add(policy)

            if (type(user.contributionPoints) != int):
                user.contributionPoints = 20
            else:
                user.contributionPoints += 20


            db.session.commit()
            flash('Policy successfully recorded. 20 points added to score!')
        else:
            flash('Policy unsuccessfully recorded')

        return redirect(url_for('index'))


    return render_template('user.html', user=user, tupList = tupList, form = form, contributionPoints = user.contributionPoints)


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

from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, Response, send_from_directory, send_file
from shiftexchange import app, db, login_manager
from flask_login import LoginManager, current_user, login_required, login_user, logout_user, UserMixin, AnonymousUser, confirm_login, fresh_login_required
from models import User, Shift
import json, math



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    if current_user.is_active():
        all_users = User.query.all()
        available_shifts = Shift.query.all()
        posted_shifts = current_user.shifts_posted
        claimed_shifts = current_user.shifts_claimed
        return render_template('demo.html', all_users=all_users,available_shifts=available_shifts,posted_shifts=posted_shifts,claimed_shifts=claimed_shifts)
    else:
        return redirect(url_for('login'))
    


@app.route('/post_shift', methods=['POST'])
def post_shift():
    #print request.form
    for item in request.form:
        #print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = ''

    employer = request.form['employer']
    date = request.form['date']

    shift = Shift(poster_id=current_user.id,time=date,employer=employer)
    db.session.add(shift)
    db.session.commit()

    return redirect(url_for('demo'))
    
@app.route('/claim_shift', methods=['POST'])
def claim_shift():
    #print request.form
    for item in request.form:
        #print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = ''

    shift_id = request.form['shift_id']

    shift = Shift.query.filter_by(id=shift_id).first()
    shift.claimable = False
    shift.claimer_id = current_user.id
    db.session.add(shift)
    db.session.commit()

    return redirect(url_for('demo'))

@app.route('/unclaim_shift', methods=['POST'])
def unclaim_shift():
    #print request.form
    for item in request.form:
        #print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = ''

    shift_id = request.form['shift_id']

    shift = Shift.query.filter_by(id=shift_id).first()
    shift.claimable = True
    shift.claimer_id = None
    db.session.add(shift)
    db.session.commit()

    return redirect(url_for('demo'))

@app.route('/delete_shift', methods=['POST'])
def delete_shift():
    #print request.form
    for item in request.form:
        #print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = ''

    shift_id = request.form['shift_id']

    shift = Shift.query.filter_by(id=shift_id).first()
    db.session.delete(shift)
    db.session.commit()

    return redirect(url_for('demo'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    email = None
    password = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = authenticate(email, password)
        if user:
            if login_user(user):
                #do stuff
                return redirect(url_for('demo'))
        #error = "Login failed"
    return render_template('login.html', login=True, email=email, password=password)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    error = None
    email = None
    password = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = User(email,password,name)

        db.session.add(user)
        db.session.commit()

        this_user = authenticate(email, password)
        if this_user:
            if login_user(this_user):
                #do stuff
                return redirect(url_for('login'))

    return render_template('create_account.html', email=email, password=password)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user:
        return user
    else:
        return None

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(redirect(url_for('index')))


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        if user.check_password(password):
            return user
    return False
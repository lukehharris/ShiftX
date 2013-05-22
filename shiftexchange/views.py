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
    print request.form
    for item in request.form:
        print item, request.form[item]
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
    print request.form
    for item in request.form:
        print item, request.form[item]
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
    print request.form
    for item in request.form:
        print item, request.form[item]
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
    print request.form
    for item in request.form:
        print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = ''

    shift_id = request.form['shift_id']

    shift = Shift.query.filter_by(id=shift_id).first()
    db.session.delete(shift)
    db.session.commit()

    return redirect(url_for('demo'))


@app.route('/submit_demo3', methods=['POST'])
def submit_demo3():
    names = {0:''}
    income  = {0:{}}
    basic_expenses = {0:{}}
    debt_expenses = {0:{}}
    misc_expenses = {0:{}}
    debt_balances = {0:{}}
    cash_balances = {0:{}}
    rates = {0:{}}
    print request.form
    scenarios = []
    for item in request.form:
        print item, request.form[item]
        if request.form[item] == '' or request.form[item] == None:
            item_value = 0
        else:
            item_value = request.form[item].replace(",", "")
        prefix = item[:3]
        item_name = item[3:-2]
        scenario = int(item[-1])
        if scenario not in scenarios:
            names.update({scenario:''})
            income.update({scenario:{}})
            basic_expenses.update({scenario:{}})
            debt_expenses.update({scenario:{}})
            misc_expenses.update({scenario:{}})
            debt_balances.update({scenario:{}})
            cash_balances.update({scenario:{}})
            rates.update({scenario:{}})
            scenarios.append(scenario)
        if prefix == "na_":
            names[scenario] = item_value
        elif prefix == "in_":
            income[scenario].update({item_name: item_value})
        elif prefix == "be_":
            basic_expenses[scenario].update({item_name: item_value})
        elif prefix == "de_":
            debt_expenses[scenario].update({item_name: item_value})
        elif prefix == "me_":
            misc_expenses[scenario].update({item_name: item_value})
        elif prefix == "ba_":
            debt_balances[scenario].update({item_name: item_value})
        elif prefix == "cb_":
            cash_balances[scenario].update({item_name: item_value})
        elif prefix == "ra_":
            rates[scenario].update({item_name: float(item_value)/100.0})
    #print rates

    scenario_count = len(scenarios)

    d = build_demo3.build_demo3_data(names, income, basic_expenses, debt_expenses, misc_expenses, debt_balances, cash_balances, rates, scenario_count)

    if current_user.is_active():
        #remove existing scenarios
        scenarios_query = current_user.scenarios.all()
        for scenario in scenarios_query:
            db.session.delete(scenario)


        for scenario in range(0,scenario_count):
        #for scenario in range(0,1):
            new_scenario = Scenario(d[scenario])
            if scenario == 0:
                new_scenario.is_base = True
            current_user.scenarios.append(new_scenario)
        #current_user.data = d[0]
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('demo3_output_detail'))



@app.route('/demo3_output')
def demo3_output():
    if current_user.is_anonymous():
        return redirect(url_for('login'))
    scenarios_query = current_user.scenarios.all()
    scenarios = []
    for scenario in scenarios_query:
        scenarios.append(scenario.data)

    #print scenarios

    ## Chart Data and Labels ##
    Chart1_data_pts = []
    Chart1_labels = []
    for x in range(0,len(scenarios)):
        Chart1_data_pts.append([])
        for y in range(0,len(scenarios[x]['net_worth']),12):
            Chart1_data_pts[x].append(scenarios[x]['net_worth'][y])
        #for k,v in scenarios[x]['net_worth'].iteritems():
        #    Chart1_data_pts[x].append(v)
    for x in range(0,len(scenarios[0]['net_worth']),12):
        Chart1_labels.append(x)


    ## / Chart Data and Labels ##

    #return render_template('demo3_output.html', s=scenarios_query[1].data)
    return render_template('demo3_output.html', s=scenarios,Chart1_data_pts=Chart1_data_pts,Chart1_labels=Chart1_labels)




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
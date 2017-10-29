# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from pymongo import MongoClient
import operator


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
# app.run(host='0.0.0.0')
mongo = MongoClient('localhost',15984)
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def dashboard():
    coord_set = []
    comp_name = []
    comp_employee = {}
    comp_type = {}
    db = mongo.CompanyDetailTest
    col = db.company_employee
    for obj in col.find():
        lat = obj['latitude']
        long = obj['longtitude']
        name = obj['comp_name'].encode('utf-8')
        employee_num = obj['employee_quantity']
        type = obj['category'].encode('utf-8')
        coord = {'lat':lat,'lng':long}
        coord_set.append(coord)
        comp_name.append([name,employee_num])
        try:
            comp_type[type] += 1
        except:
            comp_type[type] = 1
        comp_employee[name] = employee_num
    sorted_type = sorted(comp_type.items(), key=operator.itemgetter(1))
    sorted_emp = sorted(comp_employee.items(), key=operator.itemgetter(1))
    return_dict = {'name':comp_name,'employee_num':sorted_emp,'comp_type':sorted_type,'coord':coord_set}
    return render_template('index.html',comp_bag = return_dict)
# def show_entries():
#     db = get_db()
#     cur = db.execute('select title, text from entries order by id desc')
#     entries = cur.fetchall()
#     return render_template('show_entries.html', entries=entries)

@app.route('/category')
def show_category():
    categoryDic = {}
    categoryList = []
    db=mongo.CompanyDetailTest
    col = db.company_employee
    for obj in col.find():
        category = obj['category'].encode('utf-8')
        employee_num = obj['employee_quantity']
        categoryDic[category] += employee_num
    categoryList = sorted(categoryDic.iteritems(), key=lambda d: d[1], reverse=True)
    return


@app.route('/chart')
def show_chart():
    db = mongo.CompanyDetailTest
    col = db.company_employee
    type_quan = {}
    type_emp = {}
    pie_data = []
    bar_data = [[],[]]
    zone_company = {}
    zone_employee = {}
    total_employee = 0
    for obj in col.find():
        type = obj['division_code'].encode('utf-8')
        emp = obj['employee_quantity']
        zone = obj['zone']
        try:
            zone_company[zone] += 1
            zone_employee[zone] += emp
            type_quan[type] += 1
            type_emp[type] += emp
            total_employee += emp
        except:
            zone_company[zone] = 1
            zone_employee[zone] = emp
            type_quan[type] = 1
            type_emp[type] = emp
            total_employee += emp
    zone_company_list = [10*v for k, v in zone_company.iteritems()]
    zone_employee_list = [-v for k, v in zone_employee.iteritems()]
    percentage = [i*100 / float(total_employee) for i in zone_employee_list]

    sorted_type = sorted(type_quan.items(), key=operator.itemgetter(1))
    sorted_type_emp = sorted(type_emp.items(), key=operator.itemgetter(1))
    for i in range(len(sorted_type)-1,len(sorted_type)-11,-1):
        pie_data.append({'value':sorted_type[i][1],'name':sorted_type[i][0]})
    for i in range(len(sorted_type_emp)-1,0,-1):
        bar_data[0].append(sorted_type_emp[i][0])
        bar_data[1].append(sorted_type_emp[i][1])
    double_bar = [zone_company_list,zone_employee_list, percentage]
    return_dict = {'pie':pie_data,'bar':bar_data,'double_bar':double_bar}
    # return render_template('charts.html', chart_bag = return_dict)
    return render_template('charts.html', chart_bag = return_dict)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

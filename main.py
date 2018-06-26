import os
import base64
import requests
from passlib.hash import pbkdf2_sha256

from flask import Flask, render_template, request, redirect, url_for, session
from model import Donation,Donor, get_total,get_donors,get_donor_list,get_donations_list,add_donation, User
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.route('/')
def home():
    """
    Default path
    :return: all template
    """
    return redirect(url_for('all'))

def welcome():
    """
    Display welcome message to logged in user
    :return: string
    """
    msg=""
    if 'username' in session:
        user = session['username']
        msg="Welcome back, " + user
    return  msg


@app.route('/donations/')
def all():
    """
    List of all donors
    :return: donations template
    """
    donations=get_donors()
    return render_template('donations.jinja2', donations=donations,welcome=welcome())


@app.route('/create', methods=['GET', 'POST'])
def create():
    """
    If existing donor, add donation, otherwise create new donor
     - donation must be >10
    :return: GET - create template
             POST - donations template
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        try:
            val=float(request.form['donation'])
            if val<10:
                return render_template('create.jinja2',name=name,welcome=welcome())
            else:
                name=request.form['name']
                donation=float(request.form['donation'])
                msg=add_donation(name,donation)
                return redirect(url_for('all'))
        except ValueError:
            return render_template('create.jinja2', name=name,welcome=welcome())

    else:
        return render_template('create.jinja2',name="",welcome=welcome())

@app.route('/bar/')
@nocache
def bar():
    """
    Create bar chart of donor vs donation total
    :return:  bar template
    """
    data = get_total()
    labels=list([i.name for i in data])
    values=list([i.total for i in data])
    max_val=max(values)
    return render_template('bar.jinja2', values=values, labels=labels,max_val=max_val,welcome=welcome())

@app.route('/donors', methods=['GET', 'POST'])
@nocache
def donors():
    """
    Select user and display users donations
    :return:  donors template
    """
    if request.method == 'POST':
        val = request.form['target']
        donations = get_donations_list(val)
        selected_donor=val
        donor_list=get_donor_list()
        return render_template('donors.jinja2',donor_list=donor_list, donations=donations,selected_donor=selected_donor,welcome=welcome())
    else:

        donor_list=get_donor_list()
        donations=get_donations_list(donor_list[0])
        selected_donor=donor_list[0]
        return render_template('donors.jinja2', donor_list=donor_list,donations=donations,selected_donor=selected_donor,welcome=welcome())

@app.route('/pie/')
@nocache
def pie():
    """
    Create pie graph of total donations by total by donor
    :return: pie template
    """
    palette = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC"]
    data = get_total()
    values=list([i.name for i in data])
    labels=list([i.total for i in data])
    colors=palette[:4]
    return render_template('pie.jinja2', set=zip(labels,values,colors),welcome=welcome())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page. Must be one of registered users to create a donation
    :return: login template
    """
    if request.method == 'POST':
        username=request.form['name']
        passwrd=request.form['password']
        qry = User.select().where(User.name==username)
        if qry.exists():
            user = User.select().where(User.name == username).get()
            if user and pbkdf2_sha256.verify(passwrd, user.password):
                session['username'] = request.form['name']
                return redirect(url_for('all'))
        else:
            return render_template('login.jinja2', error="Incorrect username or password.",welcome=welcome())

    else:
        return render_template('login.jinja2',welcome=welcome())
@app.route('/logout')

def logout():
    """
    Delete the username session item
    :return: donations template
    """
    try:
        session.pop('username')
        return  redirect(url_for('all'))
    except:
        return redirect(url_for('all'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)



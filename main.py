import os
import base64
import requests

from flask import Flask, render_template, request, redirect, url_for, session
from model import Donation,Donor,get_total,get_donors,get_donor_list,get_donations_list,add_donation
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime



app = Flask(__name__)
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
    :return: link to all donations
    """
    return redirect(url_for('all'))



@app.route('/donations/')
def all():
    """
    List of all donors
    :return: All donations
    """
    donations=get_donors()
    return render_template('donations.jinja2', donations=donations)




@app.route('/create', methods=['GET', 'POST'])
def create():
    """
    Create a new donor if values are appropriate
    :return:
    """
    if request.method == 'POST':
        name = request.form['name']
        try:
            val=float(request.form['donation'])
            if val<10:
                return render_template('create.jinja2',name=name)
            else:
                name=request.form['name']
                donation=float(request.form['donation'])
                msg=add_donation(name,donation)
                return redirect(url_for('all'))
        except ValueError:
            return render_template('create.jinja2', name=name)

    else:
        return render_template('create.jinja2',name="")





@app.route('/bar/')
@nocache
def bar():
    data = get_total()
    labels=list([i.name for i in data])
    values=list([i.total for i in data])
    max_val=max(values)
    return render_template('bar.jinja2', values=values, labels=labels,max_val=max_val)

@app.route('/donors', methods=['GET', 'POST'])
@nocache
def donors():
    if request.method == 'POST':
        val = request.form['target']
        donations = get_donations_list(val)
        selected_donor=val
        donor_list=get_donor_list()
        return render_template('donors.jinja2',donor_list=donor_list, donations=donations,selected_donor=selected_donor)
    else:

        donor_list=get_donor_list()
        donations=get_donations_list(donor_list[0])
        selected_donor=donor_list[0]
        return render_template('donors.jinja2', donor_list=donor_list,donations=donations,selected_donor=selected_donor)

@app.route('/pie/')
@nocache
def pie():
    palette = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC"]
    data = get_total()
    values=list([i.name for i in data])
    labels=list([i.total for i in data])
    colors=palette[:4]
    return render_template('pie.jinja2', set=zip(labels,values,colors))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)



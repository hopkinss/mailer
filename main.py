import os
import base64
import requests

from flask import Flask, render_template, request, redirect, url_for, session
from model import Donation,Donor,get_total



app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':

        if request.form['name']=='':
            return redirect(url_for('all'))

        donor=Donor(name=request.form['name'])
        donor.save()
        Donation(donor=donor, value= float(request.form['donation'])).save()
        return redirect(url_for('all'))
    else:
        return render_template('create.jinja2')

@app.route('/bar/')
def bar():
    data = get_total()
    labels=list([i.name for i in data])
    values=list([i.total for i in data])
    max_val=max(values)
    return render_template('bar.jinja2', values=values, labels=labels,max_val=max_val)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)




from flask import render_template, redirect, request

from application import db, app
from application.models import *
from application.forms import *

from sqlalchemy import create_engine

import json, os

@app.route('/')
def list_cat_items():
    categories = session.query(Categories).all()
    latest_items = session.query(Items).order_by(Items.create_at.desc()).limit(10).all()
    return render_template('homepage.html', 
                            categories = categories, 
                            latest_items = latest_items)

@app.route('/cats', methods=['GET', 'POST'])
def add_a_cat():
    pass

@app.route('/items', methods=['GET', 'POST'])
def add_an_item():
    form = ItemForm(request.form)
    if request.method == 'GET':
        return render_template('additem.html', form=form)
    if request.method == 'POST':
        pass



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
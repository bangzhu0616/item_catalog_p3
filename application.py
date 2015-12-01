
from flask import render_template, redirect, request

from application import db, app
from application.models import *
from application.forms import *

from sqlalchemy import create_engine

import json, os

if not os.path.exists('./database.db'):
    db.create_all()

session = db.session

@app.route('/')
def list_cat_items():
    categories = session.query(Categories).all()
    latest_items = session.query(Items).order_by(Items.create_at.desc()).limit(10).all()
    return render_template('homepage.html', 
                            categories = categories, 
                            items = latest_items,
                            cat_name = 'Latest')

@app.route('/cats', methods=['GET', 'POST'])
def add_a_cat():
    form = CatForm(request.form)
    if request.method == 'GET':
        return render_template('addcat.html', form=form)
    if request.method == 'POST' and form.validate():
        new_cat = Categories(name=form.name.data)
        session.add(new_cat)
        session.commit()
        session.close()
        return redirect('/')

@app.route('/items', methods=['GET', 'POST'])
def add_an_item():
    form = ItemForm(request.form)
    if request.method == 'GET':
        return render_template('additem.html', form=form)
    if request.method == 'POST' and form.validate():
        new_item = Items(name=form.name.data,
                        description=form.description.data,
                        cat=form.cat.data.id)
        session.add(new_item)
        session.commit()
        session.close()
        return redirect('/')

@app.route('/catalog/<path:cat_name>/items')
def cat_items(cat_name):
    categories = session.query(Categories).all()
    items = session.query(Items).order_by(Items.create_at.desc()).all()
    count = len(items)
    return render_template('homepage.html',
                            categories = categories,
                            items = items,
                            cat_name = cat_name,
                            item_count = str(count)+' items')

@app.route('/catalog/<path:cat_name>/<path:item_name>')
def show_item(cat_name, item_name):
    cat = session.query(Categories).filter_by(name=cat_name).one()
    cat_id = cat.id
    item = session.query(Items).filter_by(name=item_name, cat=cat_id).one()
    return render_template('item.html', item=item)



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
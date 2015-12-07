from flask import render_template, redirect, request
from application import app, db
from application.models import Base, Categories, Items, Accounts
from application.forms import ItemForm, CatForm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def list_cat_items():
    categories = session.query(Categories).all()
    latest_items = session.query(Items).order_by(Items.create_at.desc()).limit(10).all()
    return render_template('homepage.html', 
                            categories = categories, 
                            items = latest_items,
                            cat_name = 'Latest')

def add_a_cat():
    form = CatForm(request.form)
    if request.method == 'GET':
        return render_template('addcat.html', form=form)
    if request.method == 'POST' and form.validate():
        new_cat = Categories(name=form.name.data)
        session.add(new_cat)
        session.commit()
        return redirect('/')

def add_an_item():
    form = ItemForm(request.form)
    if request.method == 'GET':
        cats = session.query(Categories).all()
        return render_template('additem.html', form=form, current_cat='', categories=cats, new_item=True)
    if request.method == 'POST' and form.validate():
        cat_name = request.form['category']
        cat_id = session.query(Categories).filter_by(name=cat_name).one().id
        new_item = Items(name=form.name.data,
                        description=form.description.data,
                        cat=cat_id)
        session.add(new_item)
        session.commit()
        return redirect('/')

def cat_items(cat_name):
    categories = session.query(Categories).all()
    cat_id = session.query(Categories).filter_by(name=cat_name).one().id
    items = session.query(Items).filter_by(cat=cat_id).order_by(Items.create_at.desc()).all()
    count = len(items)
    return render_template('homepage.html',
                            categories = categories,
                            items = items,
                            cat_name = cat_name,
                            item_count = str(count)+' items')

def show_item(cat_name, item_name):
    cat = session.query(Categories).filter_by(name=cat_name).one()
    cat_id = cat.id
    item = session.query(Items).filter_by(name=item_name, cat=cat_id).one()
    return render_template('item.html', item=item)

def del_item(cat_name, item_name):
    if request.method == 'GET':
        return render_template('deleteitem.html')
    if request.method == 'POST':
        cat = session.query(Categories).filter_by(name=cat_name).one()
        cat_id = cat.id
        item = session.query(Items).filter_by(name=item_name, cat=cat_id).one()
        session.delete(item)
        session.commit()
        return redirect('/catalog/%s/items' % cat_name)

def edit_item(cat_name, item_name):
    cat = session.query(Categories).filter_by(name=cat_name).one()
    cat_id = cat.id
    item = session.query(Items).filter_by(name=item_name, cat=cat_id).one()
    if request.method == 'GET':
        form = ItemForm(name=item.name, description=item.description)
        cats = session.query(Categories).all()
        return render_template('additem.html', form=form, current_cat=cat_name, categories=cats, new_item=False)
    if request.method == 'POST':
        form = ItemForm(request.form)
        cat_name = request.form['category']
        cat_id = session.query(Categories).filter_by(name=cat_name).one().id
        item.name = form.name.data
        item.description = form.description.data
        item.cat = cat_id
        session.add(item)
        session.commit()
        print '/catalog/%s/%s' %(cat_name, item_name)
        return redirect('/catalog/%s/%s' %(cat_name, item_name) )


from flask import render_template, redirect, request, jsonify, make_response, flash
from application import app, db
from application.models import Base, Categories, Items, Accounts
from application.forms import ItemForm, CatForm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json, requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def logout():
    pass

def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
    
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

def signup():
    pass

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
                            item_count = '('+str(count)+' items)')

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

def catalog_api():
    cats = session.query(Categories).all()
    return jsonify(Categories_Count=len(cats), Categories=[i.serialize for i in cats])


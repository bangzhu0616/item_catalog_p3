from application import db, app
from application.models import *
from application.forms import *
from application.functions import *

from sqlalchemy import create_engine

import json, os

engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))

if not os.path.exists('./database.db'):
    Base.metadata.create_all(engine)

app.add_url_rule('/', view_func=list_cat_items)
app.add_url_rule('/cats', view_func=add_a_cat, methods=['GET', 'POST'])
app.add_url_rule('/items', view_func=add_an_item, methods=['GET', 'POST'])
app.add_url_rule('/catalog/<path:cat_name>/items', view_func=cat_items)
app.add_url_rule('/catalog/<path:cat_name>/<path:item_name>', view_func=show_item)
app.add_url_rule('/catalog/<path:cat_name>/<path:item_name>/delete', view_func=del_item, methods=['GET', 'POST'])
app.add_url_rule('/catalog/<path:cat_name>/<path:item_name>/edit', view_func=edit_item, methods=['GET', 'POST'])

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
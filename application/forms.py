from wtforms import Form, TextField, SelectField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from models import Categories, session

def get_cats():
    cats = session.query(Categories).all()
    return [i.name for i in cats]

class ItemForm(Form):
    title = TextField('Title', [validators.required(), validators.Length(min=1, max=20)])
    description = TextField('Description')
    # cat = QuerySelectField('Category', get_label='name', query_factory=lambda: Categories.query.all() )
    cat = SelectField('Category', choices=[(catname, catname) for catname in get_cats()])
from wtforms import Form, TextField, SelectField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from models import Categories, Items

def get_cats():
    # cats = session.query(Categories).all()
    # return [i.name for i in cats]
    return Categories.query

class ItemForm(Form):
    name = TextField('Title', [validators.required(), validators.Length(min=1, max=20)])
    description = TextField('Description')
    # cat = SelectField('Category', choices=[(catname, catname) for catname in get_cats()])
    cat = QuerySelectField('Category', query_factory=get_cats, get_label='name', allow_blank=False)

class CatForm(Form):
    name = TextField('Name', [validators.required(), validators.Length(min=1, max=20)])

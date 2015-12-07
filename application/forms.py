from wtforms import Form, TextField, SelectField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class ItemForm(Form):
    name = TextField('Title', [validators.required(), validators.Length(min=1, max=20)])
    description = TextField('Description')

class CatForm(Form):
    name = TextField('Name', [validators.required(), validators.Length(min=1, max=20)])

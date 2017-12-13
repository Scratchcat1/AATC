from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    Username = wtforms.StringField('Username', validators=[DataRequired()])
    Password = wtforms.StringField('Password', validators=[DataRequired()])
    
    
class DynoField(wtforms.Form):
    name = wtforms.TextField()

class DynoForm(FlaskForm):
    fields = wtforms.FieldList(wtforms.FormField(DynoField),min_entries = 1)

def update_form(fields):
    class MyForm(FlaskForm):
        pass
    
    for item in fields:
        setattr(MyForm,item["name"],item["form"])
    print(MyForm.__dict__)

    return MyForm()

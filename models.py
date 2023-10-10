#from wtforms.form import Form
from flask_login import UserMixin
from datetime import datetime
from wtforms.fields import StringField,EmailField,SubmitField
from wtforms.validators import DataRequired,length
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ckeditor import CKEditor

login_manager = LoginManager()
db = SQLAlchemy()
csrf = CSRFProtect()
ckeditor = CKEditor()



class LoginForm(FlaskForm):
    email = EmailField('Email', [DataRequired(), length(max=30)])
    password = StringField('Password', [DataRequired(), length(max=30)])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    name = StringField('Name', [DataRequired(), length(max=30)])
    email = EmailField('Email', [DataRequired(), length(max=30)])
    password = StringField('Password', [DataRequired(), length(max=30)])
    submit = SubmitField('Signup')
#     For the login html
# {% if form.csrf_token.errors %}
#         <div class="warning">You have submitted an invalid CSRF token</div>
#     {% endif %}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    post_owner_email = db.Column(db.String(1000))
    title = db.Column(db.String(1000), unique=True)
    subtitle = db.Column(db.String(1000), unique=True)
    body = db.Column(db.String())
    post_by = db.Column(db.String(1000))
    post_date = db.Column(db.String(100))
    post_img_url = db.Column(db.String())


def post_day():
    date = datetime.now()
    year = date.strftime("%Y")
    month = date.strftime("%B")
    day = date.strftime("%d")
    if len(day) == 2 and day[0] == "0":
        day = day[1]
    if (day[-1] == "1" and len(day) == 1) or (day[-1]=="1" and len(day)>1 and day[-2]!="1"):
        sufx = "st"
    elif (day[-1] == "2" and len(day) == 1) or (day[-1]=="2" and len(day)>1 and day[-2]!="1"):
        sufx = "nd"
    elif (day[-1] == "3" and len(day) == 1) or (day[-1]=="3" and len(day)>1 and day[-2]!="1"):
        sufx = "rd"
    else:
        sufx = "th"
    today = f"{day}{sufx} {month}, {year}"
    #print(today)
    return today
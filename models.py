#from wtforms.form import Form
from flask_login import UserMixin
from wtforms.fields import StringField,EmailField,SubmitField
from wtforms.validators import DataRequired,length
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

login_manager = LoginManager()
db = SQLAlchemy()
dbp = SQLAlchemy()
csrf = CSRFProtect()



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


class Post(dbp.Model):
    id = dbp.Column(dbp.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    title = dbp.Column(dbp.String(1000), unique=True)
    subtitle = dbp.Column(dbp.String(1000), unique=True)
    body = dbp.Column(dbp.String(1000))
    post_by = dbp.Column(dbp.String(1000))
    post_date = dbp.Column(dbp.String(100))
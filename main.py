from smtplib import SMTP
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import LoginForm,db,User,SignupForm,login_manager,Post,csrf,post_day




URL = "https://api.npoint.io/eafe5d9a08398126aa2f"

app = Flask(__name__)
app.secret_key = "Any thing here"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)
csrf.init_app(app)

login_manager.login_view = 'login'
login_manager.init_app(app)


res = requests.get(URL).json()
resp = res
#print(resp)



@app.route('/')
def home():
    # data = resp
    data = Post.query.all()
    return render_template("index.html", data=data)


@app.route('/about')
def about():
    data = resp
    return render_template("about.html",data=data)


@app.route('/post/<i_d>')
#@login_required
def view_post(i_d):
    view_data = {}
    data = Post.query.get(int(i_d))
    print(data.id)
    print(data.title)
    #Read Data from SQLlite DB
    if data.id == int(i_d):
        view_data["title"] = data.title
        view_data["subtitle"] = data.subtitle
        view_data["body"] = data.body
        view_data["post_by"] = data.post_by
        view_data["post_date"] = data.post_date
    # Read Data from npoint API
    #data = resp
    # for each_post in data:
    #     if each_post["id"] == int(i_d):
    #         view_data["title"] = each_post["title"]
    #         view_data["subtitle"] = each_post["subtitle"]
    #         view_data["body"] = each_post["body"]
    #         view_data["post_by"] = each_post["post_by"]
    #         view_data["post_date"] = each_post["post_date"]
    return render_template("post.html", contxt=view_data)


@app.route("/addpost", methods = ["POST","GET"])
#@login_required
def add_post():
    db.create_all()
    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        body = request.form["content"]
        post_by = request.form["author"]
        post_date = post_day() # request.form["post_date"]
        new_post = Post(title=title, subtitle=subtitle, body=body, post_by=post_by, post_date=post_date)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_post.html")




@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use this in the query for the user
    return User.query.get(int(user_id))


@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = form.password.data
        rem = request.form.get("remember")
        if rem:
            remember = True
        else:
            remember = False
        #check and authenticate
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.")
            return redirect(url_for('login'))
        login_user(user, remember=remember)
        return redirect(url_for('home'))
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


#Add user to database would be:
@app.route("/signup", methods=["POST","GET"])
def signup():
    db.create_all()
    form = SignupForm()
    if request.method == "POST" and form.validate():
        email = form.email.data
        name = request.form["name"]
        password = form.password.data   #request.form["password"]
        #Query database to check if the user exist
        user = User.query.filter_by(email=email).first()
        if user:
            flash("User exist! Please choose a different user.")
            return redirect(url_for('signup'))
        new_user = User(email=email,password=generate_password_hash(password, method='sha256'),name=name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return render_template('signup.html', form=form)


@app.route('/contact',methods = ["GET","POST"])
def contact():
    data = {"contact": "Contact Me", "question": "Any question? I will answer it."}
    if request.method == "POST":
        name = request.form["Name"]
        email = request.form["Email"]
        phone = request.form["Phone"]
        msg = request.form["Message"]
        email_msg = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {msg}"
        my_email = "dimis378@gmail.com"
        my_pass = "axzxxcnfzskdtsha"
        with SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_pass)
            connection.sendmail(
                from_addr=my_email,
                to_addrs='gudydymys@yahoo.ca',
                msg=f"Subject:One Webform Completed\n\n{email_msg}"
            )
        #print(email_msg)
        data = {"contact": "Successfully sent your message", "question": "Any question? I will answer it."}
        return render_template("contact.html", data=data)
    return render_template("contact.html",data=data)







if __name__ == "__main__":
    app.run(debug=True)

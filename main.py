import re
import os
from smtplib import SMTP
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import res, LoginForm, db, User, SignupForm, login_manager, Post, csrf, post_day, ckeditor, Comment, gravatar


resp = res
# print(resp)
app = Flask("Dim'sBlog")
app.secret_key = "vg6yji98ujklp0iuhgfde45fgko09iklp" #os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] =  "sqlite:///db.sqlite"# os.environ.get("DB_URI") #, "sqlite:///db.sqlite")
app.config['CKEDITOR_PKG_TYPE'] = "basic"
app.config['GRAVATAR_SIZE'] = 40
app.config['GRAVATAR_RATING'] = 'g'
app.config['GRAVATAR_DEFAULT'] = 'retro'
app.config['GRAVATAR_FORCE_DEFAULT'] = False
app.config['GRAVATAR_FORCE_LOWER'] = False
app.config['GRAVATAR_USE_SSL'] = False
app.config['GRAVATAR_BASE_URL'] = None
login_manager.login_view = 'login'
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
ckeditor.init_app(app)
gravatar.init_app(app)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # data = resp
    data = Post.query.order_by(Post.id.desc()).limit(3).all() #Displays the first three data.
    return render_template("index.html", data=data)

@app.route('/olderpost')
def older_post():
    data = Post.query.order_by(Post.id.desc()).all()
    return render_template("index.html", data=data)


@app.route('/about')
def about():
    data = resp
    return render_template("about.html",data=data)


@app.route('/post/<i_d>',methods=["POST","GET"])
#@login_required
def view_post(i_d):
    view_data = {}
    #Add comment
    if request.method == "POST":
        post_reviewd = Post.query.get(int(i_d))
        commenter = User.query.filter_by(email=current_user.email).first()
        comment_body = request.form.get('ckeditor')  # request.form["content"] #request.form.get('ckeditor')
        clean = re.compile('<.*?>')
        comment_body = re.sub(clean, '', comment_body)
        new_comment = Comment(text=comment_body,commenter=commenter, post_reviewed=post_reviewd)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("home"))
    # Read Data from SQLlite DB
    data = Post.query.get(int(i_d))
    if data.id == int(i_d):
        view_data["id"] = data.id
        view_data["title"] = data.title
        view_data["subtitle"] = data.subtitle
        view_data["body"] = data.body
        view_data["post_by"] = data.post_by
        view_data["post_date"] = data.post_date
        view_data["post_img_url"] = data.post_img_url
        view_data["blog_comments"] = data.blog_post
        #view_data["blog_commented"] = data.blog_post
        # for each_blog_post in data.blog_post:
        #     print(each_blog_post.text)
        #     print(each_blog_post.commenter.email)
        if current_user.is_authenticated:
            view_data["email"] = data.post_owner.email
            if current_user.email.lower() == view_data["email"].lower():
            #if int(current_user.id) == 1:
                post_author = True
            else:
                post_author = False
            view_data["post_author"] = post_author
    # Read Data from npoint API
    #data = resp
    # for each_post in data:
    #     if each_post["id"] == int(i_d):
    #         view_data["title"] = each_post["title"]
    #         view_data["subtitle"] = each_post["subtitle"]
    #         view_data["body"] = each_post["body"]
    #         view_data["post_by"] = each_post["post_by"]
    #         view_data["post_date"] = each_post["post_date"]
    return render_template("view_post.html", contxt=view_data)


@app.route("/addpost", methods = ["POST","GET"])
@login_required
def add_post():
    view_data = {}
    #db.create_all() at the app_context above
    ttle = {"title":"New", "url":"https://images.unsplash.com/photo-1450101499163-c8848c66ca85?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjR8fGNvbXBhbnl8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60"}
    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        body = request.form.get('ckeditor') #request.form["content"] #request.form.get('ckeditor')
        clean = re.compile('<.*?>')
        body = re.sub(clean, '', body)
        #print(body)
        post_by = request.form["author"]
        post_owner = User.query.filter_by(email=current_user.email).first()
        post_img_url = request.form["url"]
        post_date = post_day() # request.form["post_date"]
        new_post = Post(title=title, subtitle=subtitle, body=body, post_by=post_by, post_date=post_date, post_img_url=post_img_url, post_owner=post_owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    view_data["id"] = ""
    view_data["title"] = ""
    view_data["subtitle"] = ""
    view_data["body"] = ""
    view_data["post_by"] = ""
    view_data["post_date"] = ""
    view_data["post_img_url"] = ""
    return render_template("add_post.html",contxt=view_data, title = ttle)


@app.route("/editpost/<i_d>", methods = ["GET","POST"])
@login_required
def edit_post(i_d):
    view_data = {}
    id=int(i_d)
    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        body = request.form.get("ckeditor")
        clean = re.compile('<.*?>')
        body = re.sub(clean, '', body)
        post_by = request.form["author"]
        post_img_url = request.form["url"]
        #post_date = post_day() # request.form["post_date"]
        # Query
        data = Post.query.get(id)  # Query Db using id
        data.title=title
        data.subtitle = subtitle
        data.post_img_url=post_img_url
        data.body=body
        data.post_by=post_by
        db.session.commit()
        return redirect(url_for("home"))
    # Read Data from SQLlite DB
    data = Post.query.get(id)
    if data.id == id:
        view_data["id"] = data.id
        view_data["title"] = data.title
        view_data["subtitle"] = data.subtitle
        view_data["body"] = data.body
        view_data["post_by"] = data.post_by
        view_data["post_date"] = data.post_date
        view_data["post_img_url"] = data.post_img_url
    ttle = {"title":"Edit","url": view_data["post_img_url"]}
    return render_template("edit_post.html", contxt=view_data, title = ttle)


@app.route("/delete/<i_d>")
@login_required
def delete_post(i_d):
    id=int(i_d)
    data = Post.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use this in the query for the user
    return User.query.get(int(user_id)) #User.query.get_or_404(int(user_id))


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
        if not user:
            flash("User does not exist. Please Signup")
            return redirect(url_for('signup'))
        elif not check_password_hash(user.password, password):
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
    #db.create_all()
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
        # hash_and_salted_password = generate_password_hash(
        #     request.form.get('password'),
        #     method='pbkdf2:sha256',
        #     salt_length=8 )   #This can be used to hae more secured password.
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        login_user(user)
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
        my_email = os.environ.get("FROM_EMAIL")
        my_pass = os.environ.get("MY_PASS")
        with SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_pass)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=os.environ.get("SENDTO_EMAIL"),
                msg=f"Subject:One Webform Completed\n\n{email_msg}"
            )
        #print(email_msg)
        data = {"contact": "Successfully sent your message", "question": "Any question? I will answer it."}
        return render_template("contact.html", data=data)
    return render_template("contact.html",data=data)




if __name__ == "__main__":
    app.run(debug=True)

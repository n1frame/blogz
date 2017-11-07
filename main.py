from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:soccer07@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        flash(username +":"+password)
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')

        else:
             #raise Exception
             flash('User password incorrect, or user does not exist', 'error')
             return redirect('/login.html')


    return render_template('login.html')

@app.route('/signup',methods=['POST', 'GET'])
def signup():    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        is_error = False

        if len(username) < 3 or len(username) > 20:
            is_error = True
            flash("Not a valid username", "error")

        if len(password) < 3 or len(password) > 20 or password != verify:
            is_error = True
            flash("Not a valid password", "error")
    
        if existing_user:
            is_error = True
            flash("User already exists", "error")  

        if is_error:
            return render_template('/signup.html', username=username)

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')


    elif request.method == "GET":
        return render_template('signup.html')

    
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args.get('userid'):
        user_id = request.args.get('userid')
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('blog.html', blogs=blogs)

    if request.args.get("id"):
        blog_id = request.args.get("id")
        blog = Blog.query.filter_by(id=blog_id).all()

        return render_template('blog.html', blogs=blog)

    
    blogs = Blog.query.all()

    return render_template('blog.html', title="Build A Blog", blogs=blogs)

@app.route('/', methods = ['GET'])
def home():
    users = User.query.all()
    return render_template('singleuser.html', users=users)

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""

        if len(blog_title) < 1:
            title_error = "Invalid title"   

        if len(blog_body) < 1:
            body_error = "Invalid Body"

        if not title_error and not body_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog.id)
            return redirect(query_param_url)

        else:
            return render_template('newpost.html', title_error = title_error, body_error = body_error)
              
    
    

if __name__ == '__main__':
    app.run()
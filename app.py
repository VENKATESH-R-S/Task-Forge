from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI_USERS'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI_TASKS'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///users.db', 'tasks': 'sqlite:///tasks.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'cube_wealh_key'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'



#Models
# Database model for Tasks
class Todo(db.Model):
    __bind_key__ = 'tasks'
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'{self.sno} -- {self.title}'
    

# Database models for Users.
class User(db.Model, UserMixin):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Forms 
# Register form.
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# Login form.
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
# Home 
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if not current_user.is_authenticated:
        flash('Please log in first.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        data = Todo(title=title, desc=desc)
        db.session.add(data)
        db.session.commit()
    alldata = Todo.query.all()
    return render_template('index.html', alldata=alldata)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # else:
    #      print("Invalid User!") #This is just to confirm that the user is valid or not at the terminal!

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Update
@app.route('/update/<int:sno>',methods=['GET','POST','PUT'])
def update(sno):
    if request.method=='POST':
        title= request.form['title']
        desc= request.form['desc']
        tata=Todo.query.filter_by(sno=sno).first()
        tata.title=title
        tata.desc=desc
        db.session.add(tata)
        db.session.commit()
        return redirect("/")
    tata=Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',tata=tata)

# Delete
@app.route('/delete/<int:sno>',methods=['GET','POST','DELETE'])
def delete(sno):
    alldata=Todo.query.filter_by(sno=sno).first()
    db.session.delete(alldata)
    db.session.commit()
    return redirect("/")

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all(bind_key='users')
        db.create_all(bind_key='tasks')

    app.run(debug=True, port=8000)
# Use debug=True only when the code is under development.


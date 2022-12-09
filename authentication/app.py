from flask import Flask, render_template, redirect, url_for, flash, session, jsonify, make_response,request
from flask.templating import render_template_string
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from os import environ, error
import re
from datetime import timedelta
from functools import wraps
from sqlalchemy import text
from datetime import datetime
from flask_cors import CORS
import time

app = Flask(__name__)

# sql setting
app.config['SECRET_KEY'] = '\x16\xea\xefcFl\xff|\x015\xe7\x9c j?yD\xfb\x1a5Tv\xf7\xbf'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
    'dbURL') or 'mysql+mysqlconnector://is213@host.docker.internal:3306/gym_user'
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get(
#     'dbURL') or 'mysql+mysqlconnector://root@localhost:3306/gym_user'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# Avoid SQL warning
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# THIS IS IF USING flask_login cookie management
#app.config["REMEMBER_COOKIE_DURATION"] = timedelta(minutes=5)
#app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = True

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
# login settings
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(80))
    delivery = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=16)])


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=16)])
    # role = SelectField(u'role', choices=["Customer", "Driver", "Storeowner"])
    delivery =  StringField('delivery', validators=[
                            InputRequired(), Length(min=4, max=80)])


# role required for string, access control


def role_required(role: str):
    def _role_required(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                flash('role unauthorized to view, forced logout')
                # if not the correct role, logout and redirect to login view with flash message
                return login_manager.unauthorized()
                # return 'Forbidden', 403
            return f(*args, **kwargs)
        return decorated_view
    return _role_required

# role required for list, access control


def roles_required(roles: list, require_all=False):
    def _roles_required(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if len(roles) == 0:
                raise ValueError('Empty list used when requiring a role.')
            if require_all and not all(current_user.role == role for role in roles):
                return 'Forbidden', 403
                # return login_manager.unauthorized()
            elif not require_all and not any(current_user.role == role for role in roles):
                return 'Forbidden', 403
                # return login_manager.unauthorized()
            return f(*args, **kwargs)
        return decorated_view
    return _roles_required

@app.before_request
def timeout_before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(
        minutes=10)  # set 1 minutes for testing, DO NOT SET TOO LONG
    session.modified = True
    #g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated and current_user.role == "Customer":
        return render_template('customer/account.html', name=current_user.username, id=current_user.id, email=current_user.email)
    elif current_user.is_authenticated and current_user.role == "Driver":
        return render_template('driver/account.html', name=current_user.username, id=current_user.id, email=current_user.email)
    elif current_user.is_authenticated and current_user.role == "Storeowner":
        return render_template('storeowner/account.html', name=current_user.username, id=current_user.id, email=current_user.email)
    else:
        form = LoginForm()
        error = None

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=False)
                    if user.role == "Customer":
                        return redirect(url_for('customer_orders'))
                    elif user.role == "Driver":
                        return redirect(url_for('driver_account'))
                    elif user.role == "Storeowner":
                        return redirect(url_for("storeowner_account"))
            error = 'Invalid username or password'

    return render_template('login.html', form=form, error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    error = None
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,17}$"

    if form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(username=form.username.data).first()
        email = User.query.filter_by(email=form.email.data).first()
        if user or email:
            error = "username or email exist in database"
        else:
            if re.search(reg, password):
                hashed_password = generate_password_hash(
                    form.password.data, method='sha256')
                new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Customer', delivery=form.delivery.data)
                db.session.add(new_user)
                db.session.commit()

                flash('New user has been created!')
                return redirect(url_for('login'))
            else:
                error = "Bad password. At least 1 upper, 1 lower, 1 digit, 1 special(@$!#%*?&) and total of 8 to 16 character"

    return render_template('sign-up.html', form=form, error=error)


"""
Change only the app.route(), required .html pages for render_template and @role_required.

"""


@app.route('/')
def index():
    if current_user.is_authenticated and (current_user.role == "Customer" or current_user.role == "Driver"):
        return render_template('index.html', name=current_user.username, id=current_user.id, email=current_user.email)
    else:
        return render_template('index.html')


"""
General Routes

"""
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
@roles_required(['Customer', 'Driver'])
def cart():
    return render_template('cart.html', name=current_user.username, id=current_user.id, email=current_user.email,delivery=current_user.delivery)

@app.route('/checkout')
@login_required
@roles_required(['Customer', 'Driver'])
def checkout():
    return render_template('checkout.html', name=current_user.username, id=current_user.id, email=current_user.email, delivery=current_user.delivery)
"""
Customer Routes

"""

@app.route('/account')
@login_required
@role_required('Customer')  # user role required
def customer_orders():
    return render_template('customer/account.html', name=current_user.username, id=current_user.id, email=current_user.email)

"""
Storeowner section

"""

@app.route('/admin')
@login_required
@role_required('Storeowner')  # user role required
def storeowner_account():
    return render_template('storeowner/account.html', name=current_user.username, id=current_user.id, email=current_user.email)

@app.route('/admin-inventory')
@login_required
@role_required('Storeowner')  # user role required
def storeowner_inventory():
    return render_template('storeowner/inventory.html', name=current_user.username, id=current_user.id, email=current_user.email)



"""
Drivers Section

"""

@app.route('/driver-account')
@login_required
@role_required('Driver')  # user role required
def driver_account():
    return render_template('driver/account.html', name=current_user.username, id=current_user.id, email=current_user.email)

@app.route('/driver-accepted')
@login_required
@role_required('Driver')  # user role required
def driver_accepted_orders():
    return render_template('driver/accepted-order.html', name=current_user.username, id=current_user.id, email=current_user.email)

@app.route('/driver-completed')
@login_required
@role_required('Driver')  # user role required
def driver_done_orders():
    return render_template('driver/all-order.html', name=current_user.username, id=current_user.id, email=current_user.email)





if __name__ == '__main__':
    #print("This is flask for " + os.path.basename(__file__) + ": manage Login ...")
    app.run(host='0.0.0.0', port=5003, debug=True)

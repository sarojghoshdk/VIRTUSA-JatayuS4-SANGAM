# Import necessary modules from Flask and Flask-Login
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, UserMixin
from ..forms.login_form import LoginForm  # Import the LoginForm class from forms module
from ..login_users import USERS  # Import the USERS dictionary containing user data
from .. import login_manager  # Import the login manager for user session handling

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Define a User class that inherits from UserMixin for user session management
class User(UserMixin):
    def __init__(self, username):
        self.id = username  # Set the user ID to the username

# Function to load a user based on user_id
@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:  # Check if the user_id exists in the USERS dictionary
        return User(user_id)  # Return a User instance if found
    return None  # Return None if user_id is not found

# Route for user login, accepting both GET and POST requests
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instantiate the login form
    if form.validate_on_submit():  # Check if the form is submitted and valid
        username = form.username.data  # Get the username from the form data
        password = form.password.data  # Get the password from the form data
        user_info = USERS.get(username)  # Retrieve user information from USERS dictionary

        # Validate the user credentials
        if user_info and user_info['password'] == password:
            user = User(username)  # Create a User instance
            login_user(user)  # Log the user in
            session['username'] = username  # Store the username in the session
            session['branch'] = user_info.get('branch')  # Store the user's branch in the session
            session['role'] = user_info.get('role')  # Store the user's role in the session
            return redirect(url_for('auth.face_verification'))  # Redirect to face verification
        else:
            flash('Invalid username or password')  # Flash an error message for invalid credentials

    return render_template('login.html', form=form)  # Render the login template with the form

# Route for user logout, protected by login_required decorator
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('auth.login'))  # Redirect to the login page

# Route for face verification
@auth_bp.route('/face_verification')
def face_verification():
    if 'username' not in session:  # Check if the user is logged in
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in
    return render_template('face_verification.html')  # Render the face verification template


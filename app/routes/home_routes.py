# Import necessary modules from Flask framework
from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import login_required

# Create a Blueprint named 'home' for organizing routes
home_bp = Blueprint('home', __name__)

# Define the route for the index page
@home_bp.route('/')
def index():
    # Redirect users to the login page
    return redirect(url_for('auth.login'))

# Define the route for the home page, requiring user to be logged in
@home_bp.route('/home')
@login_required  # Ensure that the user is authenticated before accessing this route
def home():
    # Retrieve user information from the session
    username = session.get('username')  # Get the username from the session
    branch = session.get('branch')      # Get the branch from the session
    role = session.get('role')          # Get the role from the session
    # Render the home page template with user information
    return render_template('home.html', username=username, branch=branch, role=role)

# Define the route for the contact us page, requiring user to be logged in
@home_bp.route('/contact')
@login_required  # Ensure that the user is authenticated before accessing this route
def contact_us():
    # Render the contact us page template
    return render_template('contact_us.html')

# Importing various blueprints from different route modules
from .auth_routes import auth_bp  # Blueprint for authentication routes
from .home_routes import home_bp  # Blueprint for home-related routes
from .fd_routes import fd_bp  # Blueprint for financial data routes
from .loan_routes import loan_bp  # Blueprint for loan-related routes
from .calculator_routes import calc_bp  # Blueprint for calculator-related routes
from .chatbot_routes import chatbot_bp  # Blueprint for chatbot-related routes
from .csv_routes import csv_bp  # Blueprint for CSV handling routes
from .face_routes import face_bp  # Blueprint for face recognition routes

def register_blueprints(app):
    # Registering the authentication blueprint with the main application
    app.register_blueprint(auth_bp)  
    # Registering the home blueprint with the main application
    app.register_blueprint(home_bp)  
    # Registering the financial data blueprint with the main application
    app.register_blueprint(fd_bp)  
    # Registering the loan blueprint with the main application
    app.register_blueprint(loan_bp)  
    # Registering the calculator blueprint with the main application
    app.register_blueprint(calc_bp)  
    # Registering the chatbot blueprint with the main application
    app.register_blueprint(chatbot_bp)  
    # Registering the CSV handling blueprint with the main application
    app.register_blueprint(csv_bp)  
    # Registering the face recognition blueprint with the main application
    app.register_blueprint(face_bp)  

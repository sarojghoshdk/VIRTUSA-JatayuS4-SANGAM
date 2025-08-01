from flask import Blueprint, render_template, send_from_directory  # Import necessary modules from Flask
from flask_login import login_required  # Import login_required decorator for route protection

# Create a Blueprint named 'csv' for organizing routes related to CSV operations
csv_bp = Blueprint('csv', __name__)

# Define a route for downloading CSV data, protected by login requirement
@csv_bp.route('/csv_data_download')
@login_required  # Ensure that only logged-in users can access this route
def csv_data_download():
    return render_template('csv_data_download.html')  # Render the HTML template for CSV data download

# Define a route for downloading FD records
@csv_bp.route('/download/fd')
def download_fd():
    # Send the 'fd_records.csv' file from the current directory as an attachment
    return send_from_directory(directory='.', path='fd_records.csv', as_attachment=True)

# Define a route for downloading loan data
@csv_bp.route('/download/loan')
def download_loan():
    # Send the 'loan_data.csv' file from the 'data' directory as an attachment
    return send_from_directory('data', 'loan_data.csv', as_attachment=True)


from flask import Blueprint, render_template, request, send_file, jsonify, make_response  # Import necessary Flask modules
from flask_login import login_required  # Import login_required decorator for route protection
from ..utils.pdf_utils import generate_emi_pdf  # Import function to generate EMI PDF
from ..utils.graph_utils import generate_loan_graph  # Import function to generate loan graph
import math  # Import math module for mathematical operations
import os  # Import os module for file and directory operations

calc_bp = Blueprint('calculator', __name__)  # Create a Blueprint for the calculator module

@calc_bp.route('/re_payment_loan_calculator')  # Define route for repayment loan calculator
@login_required  # Ensure user is logged in to access this route
def repayment_index():
    return render_template('repayment_calculator.html')  # Render the repayment calculator template

@calc_bp.route('/calculate', methods=['POST'])  # Define route for loan calculation
def calculate():
    data = request.json  # Get JSON data from the request
    loan_amount = float(data['loan_amount'])  # Extract and convert loan amount to float
    tenure = int(data['tenure'])  # Extract and convert tenure to integer
    interest_rate = float(data['interest_rate'])  # Extract and convert interest rate to float

    emi, total_repayment, interest_payable, graph_file = calculate_loan(loan_amount, tenure, interest_rate)  # Call loan calculation function

    return jsonify({  # Return the results as a JSON response
        'emi': round(emi, 2),  # Round EMI to 2 decimal places
        'total_repayment': round(total_repayment, 2),  # Round total repayment to 2 decimal places
        'interest_payable': round(interest_payable, 2),  # Round interest payable to 2 decimal places
        'loan-graph': graph_file  # Include the path to the generated loan graph
    })

@calc_bp.route('/download_pdf', methods=['POST'])  # Define route for downloading the PDF
def download_pdf():
    return generate_emi_pdf()  # Call function to generate and return the EMI PDF

def calculate_loan(loan_amount, tenure, interest_rate):
    monthly_rate = (interest_rate / 100) / 12  # Calculate monthly interest rate
    tenure_months = tenure * 12  # Convert tenure from years to months

    if monthly_rate > 0:  # Check if the monthly interest rate is greater than zero
        emi = (loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / (math.pow(1 + monthly_rate, tenure_months) - 1)  # Calculate EMI using the formula
    else:
        emi = loan_amount / tenure_months  # Handle zero interest case by dividing loan amount by tenure months
    
    total_repayment = emi * tenure_months  # Calculate total repayment amount
    interest_payable = total_repayment - loan_amount  # Calculate total interest payable

    # Ensure the graph directory exists
    graph_path = "app/static/repayment_graph"  # Define the path for the graph directory
    if not os.path.exists(graph_path):  # Check if the directory does not exist
        os.makedirs(graph_path)  # Create the directory if it does not exist
    
    graph_file = os.path.join(graph_path, "loan_graph.png")  # Define the path for the graph file
    generate_loan_graph(loan_amount, interest_payable, total_repayment, output_file=graph_file)  # Generate the loan graph

    return emi, total_repayment, interest_payable, graph_file  # Return calculated values

def generate_amortization_table(loan_amount, tenure, interest_rate, emi):
    table_data = [["Year", "Opening Balance", "EMI * 12", "Interest Paid Yearly", "Principal Paid Yearly", "Closing Balance"]]  # Initialize table headers
    remaining_balance = loan_amount  # Set the initial remaining balance to the loan amount

    for year in range(1, tenure + 1):  # Loop through each year of the loan tenure
        interest_paid = remaining_balance * (interest_rate / 100)  # Calculate interest paid for the year
        principal_paid = (emi * 12) - interest_paid  # Calculate principal paid for the year

        # Ensure the final year closes exactly at 0
        if year == tenure:  # Check if it is the final year
            principal_paid = remaining_balance  # Set principal paid to remaining balance
            closing_balance = 0  # Set closing balance to zero
        else:
            closing_balance = remaining_balance - principal_paid  # Calculate closing balance

        table_data.append([  # Append the year data to the table
            year,
            f"{remaining_balance:,.0f}",  # Format opening balance
            f"{(emi * 12):,.0f}",  # Format total EMI paid in the year
            f"{interest_paid:,.0f}",  # Format interest paid
            f"{principal_paid:,.0f}",  # Format principal paid
            f"{closing_balance:,.0f}" if closing_balance > 0 else "0"  # Format closing balance or set to 0
        ])

        remaining_balance = closing_balance  # Update remaining balance for the next iteration

    return table_data  # Return the generated amortization table

@calc_bp.route('/graph')  # Define route for serving the loan graph
def loan_graph():
    graph_path = 'static/repayment_graph/loan_graph.png'  # Define the path to the loan graph
    if os.path.exists(graph_path):  # Check if the graph file exists
        response = make_response(send_file(graph_path, mimetype='image/png'))  # Create a response with the graph file
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Set cache control headers
        response.headers["Pragma"] = "no-cache"  # Set pragma header
        response.headers["Expires"] = "0"  # Set expiration header
        return response  # Return the response with the graph
    return '', 404  # Return 404 if the graph file does not exist


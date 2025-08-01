from flask import Blueprint, render_template, request, session, send_file  # Import necessary Flask components
from flask_login import login_required  # Import login_required decorator for route protection
from ..models.loan_model import predict_loan  # Import loan prediction function from model
from ..utils.email_utils import send_loan_result_email  # Import email utility for sending results
from ..utils.pdf_utils import generate_loan_pdf  # Import PDF generation utility
import pandas as pd  # Import pandas for data manipulation
from app.utils.loan_graph_utils import create_loan_graphs  # Import utility for creating loan graphs

loan_bp = Blueprint('loan', __name__)  # Create a Blueprint for loan-related routes

# Mapping for transaction and trend types to numerical values
transactions_map = {'Positive': 1, 'Negative': 0}  
trends_map = {'Favorable': 1, 'Neutral': 0, 'Unfavorable': -1}  

def categorize_customer(rate):  # Function to categorize customer based on interest rate
    if rate <= 9.0:
        return "Premium Customer", "#4B0082", "#FFFFFF"  # Return category and colors for premium customers
    elif rate <= 10.0:
        return "High-Value Customer", "#1E90FF", "#FFFFFF"  # Return category and colors for high-value customers
    elif rate <= 13.0:
        return "Standard Customer", "#E0E0E0", "#333333"  # Return category and colors for standard customers
    else:
        return "Low-Tier Customer", "#FF6B6B", "#FFFFFF"  # Return category and colors for low-tier customers

@loan_bp.route('/loan_predict_form')  # Define route for loan prediction form
@login_required  # Ensure user is logged in to access this route
def loan_index():
    return render_template('loan_index.html')  # Render the loan prediction form template

@loan_bp.route('/loan_fetch_customer', methods=['POST'])  # Define route for fetching customer data
@login_required  # Ensure user is logged in to access this route
def loan_fetch_customer():
    customer_name = request.form['customer_name']  # Get customer name from form data
    customer_id = request.form['customer_id']  # Get customer ID from form data
    df = pd.read_csv('loan_customer_data.csv')  # Load customer data from CSV file
    customer = df[(df['Customer_Name'] == customer_name) & (df['Customer_ID'] == customer_id)]  # Filter customer data
    session['customer_name'] = customer_name  # Store customer name in session
    session['customer_id'] = customer_id  # Store customer ID in session    
    if not customer.empty:  # Check if customer data is found
        data = customer.iloc[0].to_dict()  # Convert customer data to dictionary
        return render_template('loan_customer_details.html', data=data)  # Render customer details template
    else:
        return "Customer not found. Please check name and ID."  # Return error message if customer not found

@loan_bp.route('/loan_predict_res', methods=['POST'])  # Define route for loan prediction results
def loan_predict():
    # Collect data from form submission
    data = {
        "Credit_History": int(request.form['credit_history']),  # Convert credit history to integer
        "Family_Credit_History": int(request.form['family_credit_history']),  # Convert family credit history to integer
        "Risk_Rating": int(request.form['risk_rating']),  # Convert risk rating to integer
        "Age": int(request.form['age']),  # Convert age to integer
        "Customer_Relationship_Years": int(request.form['customer_relationship']),  # Convert relationship years to integer
        "Past_Transactions": request.form['past_transactions'],  # Get past transactions from form
        "Market_Trends": request.form['market_trends']  # Get market trends from form
    }

    result = predict_loan(data)  # Call the loan prediction function with collected data
    graphs = create_loan_graphs(data, result)  # Create graphs based on data and prediction result
    interest_rate = result['interest_rate']  # Extract interest rate from result
    category, bg_color, text_color = categorize_customer(interest_rate)  # Categorize customer based on interest rate

    # Store result and graphs in session for later use
    session.update({
        'eligible': result['eligible'],  # Store eligibility status
        'interest_rate': result['interest_rate'],  # Store interest rate
        'max_loan': result['max_loan'],  # Store maximum loan amount
        'reasons_table': result['reasons_table'],  # Store reasons for loan decision
        'suggestions': result.get('suggestions', []),  # Store suggestions if available
        'confidence_eligibility': result.get('confidence_eligibility', 'N/A'),  # Store confidence level
        'bar_chart_base64': graphs['bar_chart_base64']  # Store base64 representation of bar chart
    })

    # Render the loan result template with all necessary data
    return render_template(
        'loan_result.html',
        result=result,  # Pass the result data to the template
        customer_category=category,  # Pass customer category to the template
        category_color=bg_color,  # Pass background color for category
        category_text_color=text_color,  # Pass text color for category
        eligible=result['eligible'],  # Pass eligibility status to the template
        interest_rate=result['interest_rate'],  # Pass interest rate to the template
        max_loan=result['max_loan'],  # Pass maximum loan amount to the template
        reasons=result['reasons'],  # Pass reasons for loan decision to the template
        chart_data=result["chart_data"],  # Pass chart data to the template
        customer_name=session.get('customer_name', 'Unknown'),  # Pass customer name from session
        customer_id=session.get('customer_id', 'Unknown'),  # Pass customer ID from session
        loan_pie_chart_path=graphs['loan_pie_chart_path'],  # Pass path for pie chart
        donut_chart_path=graphs['donut_chart_path'],  # Pass path for donut chart
        risk_relationship_path=graphs['risk_relationship_path'],  # Pass path for risk relationship chart
        interest_trend_path=graphs['interest_trend_path'],  # Pass path for interest trend chart
        loan_bar_chart_path=graphs['loan_bar_chart_path'],  # Pass path for loan bar chart
        graph_path=graphs['bar_chart_path']  # Pass path for bar chart
    )

@loan_bp.route('/loan_download_pdf', methods=['POST'])  # Define route for downloading loan PDF
def loan_download_pdf():
    return generate_loan_pdf()  # Call function to generate and return loan PDF

@loan_bp.route('/send_loan_result_email', methods=['POST'])  # Define route for sending loan result email
def loan_send_email():
    return send_loan_result_email()  # Call function to send loan result email


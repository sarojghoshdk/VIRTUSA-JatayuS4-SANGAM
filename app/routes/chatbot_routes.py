from flask import Blueprint, render_template, request, jsonify  
from flask_login import login_required  
from ..chatbot_customer_data import customer_db  

# Create a Blueprint for the chatbot routes
chatbot_bp = Blueprint('chatbot', __name__)

# Define the route for the chatbot home page
@chatbot_bp.route('/chatbot')
@login_required  # Ensure that the user is logged in to access this route
def chatbot_home():
    return render_template("chatbot.html")  # Render the chatbot HTML template

# Define the route to get customer details
@chatbot_bp.route('/get_customer_details', methods=['POST'])  # Specify that this route accepts POST requests
def get_customer_details():
    data = request.json  # Retrieve JSON data from the request
    customer_id = data.get("id")  # Extract the customer ID from the received data
    customer = customer_db.get(customer_id)  # Fetch customer details from the database using the customer ID

    if not customer:  # Check if the customer was found
        return jsonify({"error": "Customer not found"}), 404  # Return an error message if not found

    # Return customer details in JSON format
    return jsonify({
        "name": customer["name"],  # Customer's name
        "id": customer_id,  # Customer's ID
        "credit_history": customer["credit_history"],  # Customer's credit history
        "risk_rating": customer["risk_rating"],  # Customer's risk rating
        "age": customer["age"],  # Customer's age
        "relationship_years": customer["relationship_years"],  # Years of relationship with the customer
        "past_transactions": customer["past_transactions"],  # Customer's past transactions
        "market_trends": customer["market_trends"],  # Relevant market trends for the customer
        "fd_count": len(customer["fds"]),  # Count of fixed deposits held by the customer
        "fds": customer["fds"],  # List of fixed deposits
        "loan_count": len(customer["loans"]),  # Count of loans taken by the customer
        "loans": customer["loans"]  # List of loans
    })

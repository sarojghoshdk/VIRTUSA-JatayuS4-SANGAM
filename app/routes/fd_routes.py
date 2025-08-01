# Import necessary modules 
from flask import Blueprint, render_template, request, session, send_file, send_from_directory, url_for
from flask_login import login_required
from ..utils.email_utils import send_fd_result_email
from ..utils.pdf_utils import generate_fd_pdf
import joblib
import os
from app.utils.fd_graph_utils import generate_fd_graphs
from app.utils.fd_summary_utils import generate_summary_table
#-------------FD PDF-------------------------
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import random
import csv
import base64
import pandas as pd
import numpy as np
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from sklearn.ensemble import RandomForestRegressor

# Create a Blueprint for the fixed deposit (fd) module
fd_bp = Blueprint('fd', __name__)

# Load the pre-trained machine learning pipeline for fixed deposit predictions
pipeline = joblib.load('models/fd_model/fd_pipeline.pkl')

def categorize_customer(rate):
    # Categorize customer based on the interest rate
    if rate >= 9.0:
        return "Premium Customer", "#4B0082", "#FFFFFF"  # Premium customer with specific colors
    elif rate >= 7.0:
        return "High-Value Customer", "#1E90FF", "#FFFFFF"  # High-value customer with specific colors
    elif rate >= 5.0:
        return "Standard Customer", "#E0E0E0", "#333333"  # Standard customer with specific colors
    else:
        return "Low-Tier Customer", "#FF6B6B", "#FFFFFF"  # Low-tier customer with specific colors

@fd_bp.route('/fd_predict_form')
@login_required
def fd_index():
    # Render the fixed deposit prediction form
    return render_template('fd_index.html')

@fd_bp.route('/fetch_customer_fd', methods=['POST'])
def fetch_customer_fd():
    # Retrieve customer details from the form
    name = request.form['customer_name']
    cid = request.form['customer_id']
    
    # Load customer data from CSV file
    df = pd.read_csv('customers.csv')

    # Filter customer data based on name and ID
    customer = df[(df['Customer_Name'] == name) & (df['Customer_ID'].astype(str) == cid)]
    
    if customer.empty:
        # Return error message if customer is not found
        return "Customer not found. Please check the details."

    # Extract row as dict for further processing
    customer_data = customer.iloc[0].to_dict()

    # Store customer details in session for later use
    session['customer_name'] = request.form.get('customer_name', 'Unknown')
    session['customer_id'] = request.form.get('customer_id', 'Unknown')

    # Render customer details page
    return render_template('fd_customer_details.html', customer=customer_data)

@fd_bp.route('/fd_predict_res', methods=['POST'])
def fd_predict():
    try:
        # Prepare input data for prediction
        data = {
            "Credit_History": float(request.form['credit_history']),
            "Risk_Rating": float(request.form['risk_rating']),
            "Age": float(request.form['age']),
            "Customer_Relationship_Years": float(request.form['relationship_years']),
            "Past_Transactions": request.form['transactions'],
            "Market_Trends": request.form['market_trends']
        }
        input_df = pd.DataFrame([data])  # Convert input data to DataFrame
        interest_rate = pipeline.predict(input_df)[0]  # Predict interest rate using the model
        category, bg_color, text_color = categorize_customer(interest_rate)  # Categorize customer based on interest rate
        
        # Confidence Score Calculation
        try:
            model = pipeline.named_steps['model']  # Access the model from the pipeline
            if isinstance(model, RandomForestRegressor):
                # Calculate predictions from each tree in the forest
                tree_preds = [tree.predict(pipeline.named_steps['preprocessor'].transform(input_df))[0] for tree in model.estimators_]
                std_dev = np.std(tree_preds)  # Calculate standard deviation of predictions
                confidence_score = max(0, round(100 - std_dev * 10, 2))  # Calculate confidence score
            else:
                confidence_score = "N/A"  # Not applicable for other models
        except Exception as conf_err:
            confidence_score = "Unavailable"  # Handle errors in confidence score calculation
            print("Confidence score error:", conf_err)

        # Generate summary and graphs for the prediction
        positive_reasons, negative_reasons, summary_table, total_score, favorability, overall_profile = generate_summary_table(data)
        generate_fd_graphs(interest_rate, summary_table)  # Generate graphs based on the interest rate and summary

        # Convert generated image to base64 for rendering
        with open("app/static/reasoning_chart.png", "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        # Store results in session for rendering the result page
        session.update({
            'interest_rate': f"{interest_rate:.2f}%",
            'confidence_score': confidence_score,
            'positive_reasons': positive_reasons,
            'negative_reasons': negative_reasons,
            'summary_table': summary_table,
            'total_score': total_score,
            'favorability': f"{favorability:.2f}%",
            'overall_profile': overall_profile,
            'image_base64': image_base64
        })

        # Render the result page with all relevant data
        return render_template('fd_result.html',
                               interest_rate=f"{interest_rate:.2f}%",
                               confidence_score=confidence_score,
                               customer_category=category,
                               category_color=bg_color,
                               category_text_color=text_color,
                               positive_reasons=positive_reasons,
                               negative_reasons=negative_reasons,
                               summary_table=summary_table,
                               total_score=total_score,
                               favorability=f"{favorability:.2f}%",
                               overall_profile=overall_profile,
                               image_base64=image_base64,
                               customer_name=session.get('customer_name', 'Unknown'),
                               customer_id=session.get('customer_id', 'Unknown'))
    except Exception as e:
        # Return error message if an exception occurs
        return f"Error: {e}"

@fd_bp.route('/fd_download_pdf')
@login_required
def fd_download_pdf():
    # Generate and return the fixed deposit PDF
    return generate_fd_pdf()

@fd_bp.route('/send_fd_result_email', methods=['POST'])
def fd_send_email():
    # Send the fixed deposit result via email
    return send_fd_result_email()

@fd_bp.route('/fd_application')
@login_required
def fd_application():
    # Retrieve customer details from session for the application form
    customer_name = session.get('customer_name', '')
    customer_id = session.get('customer_id', '')
    interest_rate = session.get('interest_rate', '')
    return render_template('fd_apply_form.html', customer_name=customer_name, customer_id=customer_id, interest_rate=interest_rate)

@fd_bp.route('/create_fd', methods=['POST'])
def create_fd():
    # Retrieve form data for creating a fixed deposit
    customer_name = request.form['customer_name']
    customer_id = request.form['customer_id']
    interest_rate = float(request.form['interest_rate'].replace('%', ''))  # Convert interest rate to float
    amount = float(request.form['amount'])  # Convert amount to float
    period = float(request.form['period'])  # Convert period to float
    maturity_amount = amount + (amount * interest_rate * period / 100)  # Calculate maturity amount
    fd_account_number = str(random.randint(100000, 999999))  # Generate random 6-digit FD account number
    fd_create_date = datetime.now().strftime("%d-%b-%Y")  # Get current date
    maturity_date = (datetime.now() + timedelta(days=int(period * 365))).strftime("%d-%b-%Y")  # Calculate maturity date

    # Save FD details to CSV file
    csv_file = os.path.join('app', 'fd_records.csv')
    file_exists = os.path.isfile(csv_file)  # Check if the file already exists
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)  # Create a CSV writer object
        if not file_exists:
            # Write header if the file is new
            writer.writerow(['FD Account Number', 'Customer Name', 'Customer ID', 'Interest Rate (%)', 'Amount', 'Period (Years)', 'Maturity Amount', 'FD Date', 'Maturity Date'])
        # Write FD details to the CSV file
        writer.writerow([fd_account_number, customer_name, customer_id, interest_rate, amount, period, maturity_amount, fd_create_date, maturity_date])

    # Path to save the generated PDF
    pdf_filename = f"fd_certificate_{fd_account_number}.pdf"
    pdf_path = os.path.join("app/static/fd_certificate", pdf_filename)
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))  # Create a PDF canvas
    width, height = landscape(A4)  # Get dimensions for landscape A4

    # Draw a decorative golden border on the PDF
    c.setStrokeColorRGB(218/255, 165/255, 32/255)
    c.setLineWidth(4)
    c.rect(20, 20, width - 40, height - 40)  # Draw rectangle for border

    # Add Bank Logo (adjust size and path)
    logo_path = "static/images/header.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 120, width=100, height=80, preserveAspectRatio=True)  # Add logo to PDF
    c.setFillColor(colors.black)  # Set text color to black
    c.setFont("Helvetica-Bold", 26)  # Set font for title
    c.drawCentredString(width / 2, height - 70, "SANGAM Dynamic Pricing")  # Add title to PDF
    c.setFont("Helvetica-Bold", 20)  # Set font for subtitle
    c.drawCentredString(width / 2, height - 110, "Fixed Deposit Certificate")  # Add subtitle to PDF
    c.setFont("Helvetica", 14)  # Set font for body text
    c.drawCentredString(width / 2, height - 150, "This is to certify that the following Fixed Deposit has been created")  # Add body text

    # FD Details Table
    data = [
        ['FD Account Number:', fd_account_number], 
        ['Customer Name:', customer_name],
        ['Customer ID:', customer_id],
        ['FD Amount:', f"{amount:.2f}", 'Interest Rate (%):', f"{interest_rate:.2f}%"],
        ['FD Period (Years):', period, 'Maturity Amount:', f"{maturity_amount:.2f}"],
        ['FD Creation Date:', fd_create_date, 'Maturity Date:', maturity_date]
    ]

    # Create a table for FD details
    table = Table(data, colWidths=[130, 180, 130, 180])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Set font for the table
        ('FONTSIZE', (0, 0), (-1, -1), 12),  # Set font size for the table
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),  # Add box around the table
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.grey),  # Add inner grid lines
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),  # Set background color for header
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Align text to the left
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align text to the middle
    ]))
    table.wrapOn(c, width, height)  # Wrap the table on the canvas
    table.drawOn(c, 70, height - 350)  # Draw the table on the PDF

    # Signature lines for the PDF
    c.setFont("Helvetica", 12)  # Set font for signatures
    c.line(100, 100, 300, 100)  # Draw line for Assistant Branch Manager signature
    c.drawString(150, 85, "Assistant Branch Manager")  # Add title for Assistant Branch Manager
    c.line(width - 300, 100, width - 100, 100)  # Draw line for Branch Manager signature
    c.drawString(width - 230, 85, "Branch Manager")  # Add title for Branch Manager
    c.setFont("Helvetica-Oblique", 10)  # Set font for footer
    c.setFillColor(colors.lightgrey)  # Set footer text color
    c.drawCentredString(width / 2, 50, "Generated by Dynamic Financial Pricing System - Valid for Verification")  # Add footer text
    c.save()  # Save the PDF

    # Generate URL for downloading the PDF
    pdf_url = url_for('fd.download_fd_pdf', filename=pdf_filename)
    print(pdf_url)  # Print the PDF URL for debugging

    # Render success page after FD creation
    return render_template('fd_apply_success.html',
                           customer_name=customer_name,
                           fd_account_number=fd_account_number,
                           amount=amount,
                           period=period,
                           interest_rate=interest_rate,
                           maturity_amount=maturity_amount,
                           pdf_url=pdf_url)

# ----- FD Certificate Download -----
@fd_bp.route('/download/fd_pdf/<filename>')
@login_required
def download_fd_pdf(filename):
    # Send the generated FD PDF file as an attachment
    return send_from_directory('static/fd_certificate', filename, as_attachment=True)


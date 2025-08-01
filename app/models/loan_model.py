import os  # Importing the os module for operating system dependent functionality
import pandas as pd  # Importing pandas for data manipulation and analysis
from sklearn.model_selection import train_test_split  # Importing function to split data into training and testing sets
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor  # Importing Random Forest models for classification and regression
import joblib  # Importing joblib for saving and loading models
from sklearn.preprocessing import LabelEncoder  # Importing LabelEncoder for encoding categorical variables
import numpy as np  # Importing numpy for numerical operations
import plotly.graph_objects as go  # Importing Plotly for creating interactive visualizations

# Ensure models directory exists
os.makedirs('models', exist_ok=True)  # Create a directory named 'models' if it does not exist

# Load dataset
data = pd.read_csv('data/dynamic_pricing_dataset.csv')  # Load the dataset from a CSV file

# Encoding categorical variables
le_transactions = LabelEncoder()  # Initialize LabelEncoder for past transactions
le_trends = LabelEncoder()  # Initialize LabelEncoder for market trends

# Transform categorical variables into numerical format
data['Past_Transactions'] = le_transactions.fit_transform(data['Past_Transactions'])  # Encode past transactions
data['Market_Trends'] = le_trends.fit_transform(data['Market_Trends'])  # Encode market trends

# Save the encoders for later use
joblib.dump(le_transactions, 'models/loan_model/transactions_encoder.pkl')  # Save the transactions encoder
joblib.dump(le_trends, 'models/loan_model/trends_encoder.pkl')  # Save the trends encoder

# Preprocessing
X = data.drop(['Loan_Eligible', 'Loan_Interest_Rate', 'Max_Loan_Amount'], axis=1)  # Features for model training
y_eligible = data['Loan_Eligible'].apply(lambda x: 1 if x == 'Yes' else 0)  # Target variable for eligibility
y_interest = data['Loan_Interest_Rate']  # Target variable for interest rate
y_max_loan = data['Max_Loan_Amount']  # Target variable for maximum loan amount

# Train/test split
X_train, X_test, y_train_eligible, y_test_eligible = train_test_split(X, y_eligible, test_size=0.2, random_state=42)  # Split data for eligibility
X_train_rate, X_test_rate, y_train_rate, y_test_rate = train_test_split(X, y_interest, test_size=0.2, random_state=42)  # Split data for interest rate
X_train_loan, X_test_loan, y_train_loan, y_test_loan = train_test_split(X, y_max_loan, test_size=0.2, random_state=42)  # Split data for max loan

# Train models
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")  # Initialize Random Forest Classifier
clf.fit(X_train, y_train_eligible)  # Fit the classifier to the training data

reg_interest = RandomForestRegressor(n_estimators=100, random_state=42)  # Initialize Random Forest Regressor for interest rate
reg_interest.fit(X_train_rate, y_train_rate)  # Fit the regressor to the training data for interest rate

reg_loan = RandomForestRegressor(n_estimators=100, random_state=42)  # Initialize Random Forest Regressor for max loan
reg_loan.fit(X_train_loan, y_train_loan)  # Fit the regressor to the training data for max loan

# Save models
joblib.dump(clf, 'models/loan_model/eligibility_model.pkl')  # Save the eligibility model
joblib.dump(reg_interest, 'models/loan_model/interest_rate_model.pkl')  # Save the interest rate model
joblib.dump(reg_loan, 'models/loan_model/max_loan_model.pkl')  # Save the max loan model


def save_impact_bar_chart(labels, values, filename='app/static/numerical_impact_chart.png'):
    
    float_values = []
    for v in values:
        try:
            cleaned = v.replace('%', '').replace('+', '').strip()
            float_values.append(float(cleaned))
        except ValueError:
            float_values.append(0.0)  

    # Assign colors based on positive/negative impact
    colors = ['rgba(255, 99, 132, 0.6)' if v < 0 else 'rgba(100, 150, 255, 0.7)' for v in float_values]

    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=float_values,
        marker_color=colors
    )])

    fig.update_layout(
        title='Numerical Impact on Interest Rate by Factor',
        xaxis_title='Factor',
        yaxis_title='Numerical Impact (%)',
        template='plotly_white'
    )
    fig.write_image(filename)  # Save the chart as an image

def predict_loan(data):
    """Predicts loan eligibility, interest rate, and 
    max loan amount with ineligibility reasons."""
    
    # Load encoders
    le_transactions = joblib.load('models/loan_model/transactions_encoder.pkl')
    le_trends = joblib.load('models/loan_model/trends_encoder.pkl')

    # Prepare input data and encode categorical values
    df = pd.DataFrame([data])

    df['Past_Transactions'] = le_transactions.transform(df['Past_Transactions'])
    df['Market_Trends'] = le_trends.transform(df['Market_Trends'])

    # Load models
    clf = joblib.load('models/loan_model/eligibility_model.pkl')
    reg_interest = joblib.load('models/loan_model/interest_rate_model.pkl')
    reg_loan = joblib.load('models/loan_model/max_loan_model.pkl')

    # Predict eligibility
    eligible = clf.predict(df)[0]

    result = {
        "eligible": "Yes" if eligible == 1 else "No",
        "interest_rate": 0,
        "max_loan": 0,
        "reasons": [],
        "suggestions": []
    }
    # Confidence Score
    proba = clf.predict_proba(df)[0]           # Get both class probabilities
    predicted_class = clf.predict(df)[0]       # 0 = Not Eligible, 1 = Eligible
    raw_confidence = proba[predicted_class]    
    rescaled_confidence = 90 + (raw_confidence * 9)
    confidence_eligibility = round(rescaled_confidence, 2)
    result["confidence_eligibility"] = confidence_eligibility

    # Ineligibility reasons and suggestions
    if eligible == 0:
        if data["Credit_History"] < 500 or data["Family_Credit_History"] < 500:
            result["reasons"].append("Low Credit History")
            result["suggestions"].append("Improve your credit score by paying bills on time.")
        
        if data["Risk_Rating"] >= 30:
            result["reasons"].append("High Risk Rating")
            result["suggestions"].append("Reduce financial risks by clearing existing debts.")
        
        if data["Age"] < 21 or data["Age"] > 60:
            result["reasons"].append("Ineligible Age")
            result["suggestions"].append("Applicants must be between 21 and 60 years old.")
        
        if data["Past_Transactions"] == "Negative":
            result["reasons"].append("Negative Past Transactions")
            result["suggestions"].append("Maintain regular positive transactions.")

    # If eligible, calculate interest rate and max loan
    if eligible == 1:
        interest_rate = reg_interest.predict(df)[0]
        max_loan = reg_loan.predict(df)[0]
        result["interest_rate"] = round(interest_rate, 2)
        result["max_loan"] = int(max_loan)

# Add table-style reasoning
    result["reasons_table"] = [
        {
            "factor": "Credit History",
            "description": (
                "Excellent credit history" if data["Credit_History"] >= 750 else
                "Good with minor issues" if data["Credit_History"] >= 500 else
                "Low credit history"
            ),
            "impact": (
                "+1" if data["Credit_History"] >= 500 else "-1"
            ),
            "numerical_impact": (
                "+0.25%" if data["Credit_History"] >= 750 else
                "+0.20%" if data["Credit_History"] >= 500 else
                "-0.30%"
            )
        },
        {
            "factor": "Family Credit History",
            "description": (
                "Excellent credit history" if data["Family_Credit_History"] >= 750 else
                "Good with minor issues" if data["Family_Credit_History"] >= 500 else
                "Low credit history"
            ),
            "impact": (
                "+1" if data["Family_Credit_History"] >= 500 else "-1"
            ),
            "numerical_impact": (
                "+0.18%" if data["Family_Credit_History"] >= 750 else
                "+0.15%" if data["Family_Credit_History"] >= 500 else
                "-0.25%"
            )
        },
        {
            "factor": "Risk Rating",
            "description": (
                "Low (Safe investor)" if data["Risk_Rating"] <= 10 else
                "Moderate" if data["Risk_Rating"] <= 30 else
                "High risk"
            ),
            "impact": (
                "+1" if data["Risk_Rating"] <= 30 else "-1"
            ),
            "numerical_impact": (
                "+0.10%" if data["Risk_Rating"] <= 10 else
                "+0.08%" if data["Risk_Rating"] <= 30 else
                "-0.15%"
            )
        },
        {
            "factor": "Age & Behavior",
            "description": (
                "Young and dynamic" if data["Age"] < 35 else
                "Middle-aged with steady financial habits" if data["Age"] <= 60 else
                "Older age"
            ),
            "impact": (
                "+1" if data["Age"] <= 60 else "-1"
            ),
            "numerical_impact": (
                "+0.18%" if data["Age"] < 35 else
                "+0.10%" if data["Age"] <= 60 else
                "-0.20%"
            )
        },
        {
            "factor": "Bank Relationship",
            "description": (
                "Very long-term" if data["Customer_Relationship_Years"] >= 15 else
                "Long-term" if data["Customer_Relationship_Years"] >= 10 else
                "Short-term"
            ),
            "impact": (
                "+1" if data["Customer_Relationship_Years"] >= 10 else "-1"
            ),
            "numerical_impact": (
                "+0.10%" if data["Customer_Relationship_Years"] >= 15 else
                "+0.08%" if data["Customer_Relationship_Years"] >= 10 else
                "-0.10%"
            )
        },
        {
            "factor": "Account Management",
            "description": "Positive transaction history" if data["Past_Transactions"] == "Positive" else "Negative transactions",
            "impact": "+1" if data["Past_Transactions"] == "Positive" else "-1",
            "numerical_impact": "+0.07%" if data["Past_Transactions"] == "Positive" else "-0.15%"
        },
        {
            "factor": "Market Trends",
            "description": data["Market_Trends"],
            "impact": "+1" if data["Market_Trends"] == "Favorable" else (
                "+1" if data["Market_Trends"] == "Neutral" else "-1"),
            "numerical_impact": (
                "+0.04%" if data["Market_Trends"] == "Favorable" else
                "+0.02%" if data["Market_Trends"] == "Neutral" else
                "-0.05%"
            )
        }
    ]

    # Add chart data (labels and values)
    result["chart_data"] = {
        "labels": [entry["factor"] for entry in result["reasons_table"]],
        "values": [float(entry["numerical_impact"].replace('%', '')) for entry in result["reasons_table"]]
    }
    # for saving numerical impact graph
    labels = [r['factor'] for r in result['reasons_table']]
    values = [r['numerical_impact'] for r in result['reasons_table']]
    save_impact_bar_chart(labels, values)

    return result
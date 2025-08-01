import unittest  # Importing the unittest module for creating unit tests
import joblib  # Importing joblib for loading machine learning models
import pandas as pd  # Importing pandas for data manipulation and analysis
import numpy as np  # Importing numpy for numerical operations
import os  # Importing os for interacting with the operating system

class TestLoanPrediction(unittest.TestCase):  # Defining a test case class for loan prediction

    def setUp(self):  # Method to set up the test environment
        # Load model files directly from path
        eligibility_model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'loan_model', 'eligibility_model.pkl')  # Path for eligibility model
        interest_rate_model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'loan_model', 'interest_rate_model.pkl')  # Path for interest rate model
        max_loan_model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'loan_model', 'max_loan_model.pkl')  # Path for max loan model
        transactions_encoder_model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'loan_model', 'transactions_encoder.pkl')  # Path for transactions encoder
        trends_encoder_model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'loan_model', 'trends_encoder.pkl')  # Path for trends encoder

        # Loading the models using joblib
        self.eligibility_model = joblib.load(eligibility_model_path)  # Loading eligibility model
        self.interest_model = joblib.load(interest_rate_model_path)  # Loading interest rate model
        self.max_loan_model = joblib.load(max_loan_model_path)  # Loading max loan model

        self.transactions_encoder = joblib.load(transactions_encoder_model_path)  # Loading transactions encoder
        self.trends_encoder = joblib.load(trends_encoder_model_path)  # Loading trends encoder

    def test_typical_case(self):  # Test method for a typical loan application case
        input_data = {  # Defining input data for the test
            "Credit_History": 750,  # Credit history score
            "Family_Credit_History": 720,  # Family credit history score
            "Risk_Rating": 15,  # Risk rating of the applicant
            "Age": 30,  # Age of the applicant
            "Customer_Relationship_Years": 10,  # Years of relationship with the bank
            "Past_Transactions": "Positive",  # Past transaction history
            "Market_Trends": "Favorable"  # Current market trends
        }

        df = pd.DataFrame([input_data])  # Creating a DataFrame from the input data
        df['Past_Transactions'] = self.transactions_encoder.transform(df['Past_Transactions'])  # Transforming past transactions using the encoder
        df['Market_Trends'] = self.trends_encoder.transform(df['Market_Trends'])  # Transforming market trends using the encoder

        eligible = self.eligibility_model.predict(df)[0]  # Predicting loan eligibility
        interest_rate = self.interest_model.predict(df)[0]  # Predicting interest rate
        max_loan = self.max_loan_model.predict(df)[0]  # Predicting maximum loan amount

        # Printing results for the typical case
        print("\n--- Typical Case ---")
        print("Loan Eligibility:", "Yes" if eligible == 1 else "No")  # Displaying eligibility result
        print(f"Predicted Interest Rate: {round(interest_rate, 2)} %")  # Displaying predicted interest rate
        print("Predicted Max Loan Amount:", int(max_loan))  # Displaying predicted max loan amount

        # Assertions to validate the predictions
        self.assertIn(eligible, [0, 1])  # Checking if eligibility is binary
        self.assertGreaterEqual(interest_rate, 0)  # Ensuring interest rate is non-negative
        self.assertGreaterEqual(max_loan, 0)  # Ensuring max loan amount is non-negative

    def test_edge_case_low_credit(self):  # Test method for an edge case with low credit
        input_data = {  # Defining input data for the edge case
            "Credit_History": 300,  # Low credit history score
            "Family_Credit_History": 300,  # Low family credit history score
            "Risk_Rating": 40,  # High risk rating
            "Age": 18,  # Young age of the applicant
            "Customer_Relationship_Years": 0,  # No relationship with the bank
            "Past_Transactions": "Negative",  # Negative past transaction history
            "Market_Trends": "Unfavorable"  # Unfavorable market trends
        }

        df = pd.DataFrame([input_data])  # Creating a DataFrame from the input data
        df['Past_Transactions'] = self.transactions_encoder.transform(df['Past_Transactions'])  # Transforming past transactions
        df['Market_Trends'] = self.trends_encoder.transform(df['Market_Trends'])  # Transforming market trends

        eligible = self.eligibility_model.predict(df)[0]  # Predicting loan eligibility

        # Conditional logic based on eligibility
        if eligible == 1:  # If eligible, predict interest rate and max loan
            interest_rate = self.interest_model.predict(df)[0]  # Predicting interest rate
            max_loan = self.max_loan_model.predict(df)[0]  # Predicting max loan amount
        else:  # If not eligible, set interest rate and max loan to zero
            interest_rate = 0
            max_loan = 0

        # Printing results for the edge case
        print("\n--- Edge Case (Low Credit) ---")
        print("Loan Eligibility:", "Yes" if eligible == 1 else "No")  # Displaying eligibility result
        print(f"Predicted Interest Rate: {round(interest_rate, 2)} %")  # Displaying predicted interest rate
        print("Predicted Max Loan Amount:", int(max_loan))  # Displaying predicted max loan amount

        # Assertions to validate the predictions
        self.assertIn(eligible, [0, 1])  # Checking if eligibility is binary
        if eligible == 1:  # If eligible, validate interest rate and max loan
            self.assertGreater(interest_rate, 0)  # Ensuring interest rate is positive
            self.assertGreater(max_loan, 0)  # Ensuring max loan amount is positive
        else:  # If not eligible, validate interest rate and max loan are zero
            self.assertEqual(interest_rate, 0)  # Ensuring interest rate is zero
            self.assertEqual(max_loan, 0)  # Ensuring max loan amount is zero

    def test_prediction_with_invalid_data(self):  # Test method for handling invalid data
        invalid_data = {  # Defining invalid input data
            "Credit_History": 700,  # Valid credit history score
            "Family_Credit_History": 680,  # Valid family credit history score
            "Risk_Rating": 25,  # Valid risk rating
            "Age": "Thirty",  # Invalid type for age
            "Customer_Relationship_Years": 5,  # Valid years of relationship
            "Past_Transactions": "Positive",  # Valid past transaction history
            "Market_Trends": "Favorable"  # Valid market trends
        }

        try:
            df = pd.DataFrame([invalid_data])  # Creating a DataFrame from the invalid input data
            df['Past_Transactions'] = self.transactions_encoder.transform(df['Past_Transactions'])  # Transforming past transactions
            df['Market_Trends'] = self.trends_encoder.transform(df['Market_Trends'])  # Transforming market trends
            self.eligibility_model.predict(df)  # Attempting to predict eligibility
            self.fail("Expected ValueError was not raised.")  # Failing the test if no error is raised

        except Exception as e:  # Catching any exceptions raised
            # Printing results for the invalid data case
            print("\n--- Invalid Data Case ---")
            print(f"Raised Exception: {type(e).__name__} - {str(e)}")  # Displaying the exception type and message
            self.assertIsInstance(e, ValueError)  # Asserting that the exception is a ValueError

if __name__ == "__main__":  # Entry point for the script
    unittest.main()  # Running the unit tests


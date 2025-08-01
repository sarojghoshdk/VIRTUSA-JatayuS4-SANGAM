import unittest
import joblib
import pandas as pd
import os

class TestFDInterestRatePrediction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nSetting up FD pipeline...")
        # Constructing the model path by navigating to the appropriate directory
        model_path = os.path.join(os.path.dirname(__file__), '..', '..','models', 'fd_model', 'fd_pipeline.pkl')
        # Loading the pre-trained model pipeline from the specified path
        cls.pipeline = joblib.load(model_path)
        print("FD pipeline loaded successfully.\n")

    def test_prediction_with_valid_data(self):
        print("\nRunning test: test_prediction_valid_input")
        # Creating a DataFrame with valid input data for prediction
        sample_data = pd.DataFrame([{
            "Credit_History": 750.0,
            "Risk_Rating": 15.0,
            "Age": 35.0,
            "Customer_Relationship_Years": 5.0,
            "Past_Transactions": "Positive",
            "Market_Trends": "Favorable"
        }])

        # Making a prediction using the loaded pipeline
        result = self.pipeline.predict(sample_data)
        print(f"Prediction for valid input: {result}%")
        # Asserting that the result is not None
        self.assertIsNotNone(result)
        # Asserting that the result is of type float
        self.assertIsInstance(result[0], float)
        # Asserting that the predicted interest rate is positive
        self.assertGreater(result[0], 0)  # Interest rate should be positive

    def test_prediction_with_edge_case_data(self):
        # Edge case: Low credit, high risk
        print("\nRunning test: test_prediction_edge_case")
        # Creating a DataFrame with edge case input data for prediction
        sample_data = pd.DataFrame([{
            "Credit_History": 300.0,
            "Risk_Rating": 90.0,
            "Age": 78.0,
            "Customer_Relationship_Years": 0.0,
            "Past_Transactions": "Negative",
            "Market_Trends": "Unfavorable"
        }])

        # Making a prediction using the loaded pipeline
        result = self.pipeline.predict(sample_data)
        print(f"Prediction for edge case: {result}%")
        # Asserting that the result is not None
        self.assertIsNotNone(result)
        # Asserting that the result is of type float
        self.assertIsInstance(result[0], float)

    def test_prediction_with_invalid_data(self):
        print("\nRunning test: test_prediction_with_invalid_data")
        # Creating a DataFrame with invalid input data for prediction
        sample_data = pd.DataFrame([{
            "Credit_History": "invalid",  # Non-numeric
            "Risk_Rating": -5,
            "Age": None,
            "Customer_Relationship_Years": "five",
            "Past_Transactions": 123,  # Invalid
            "Market_Trends": "Unknown"
        }])
        # Asserting that an exception is raised when predicting with invalid data
        with self.assertRaises(Exception) as context:
            self.pipeline.predict(sample_data)

        print("Raised Exception:", context.exception)

if __name__ == '__main__':
    unittest.main()

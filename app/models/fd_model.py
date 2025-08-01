import pandas as pd  # Importing the pandas library for data manipulation and analysis
import numpy as np  # Importing the numpy library for numerical operations
from sklearn.model_selection import train_test_split  # Importing function to split data into training and testing sets
from sklearn.preprocessing import StandardScaler, OneHotEncoder  # Importing preprocessing tools for scaling and encoding
from sklearn.compose import ColumnTransformer  # Importing ColumnTransformer for applying different preprocessing to different columns
from sklearn.pipeline import Pipeline  # Importing Pipeline to streamline the workflow
from sklearn.ensemble import RandomForestRegressor  # Importing RandomForestRegressor for regression tasks
import joblib  # Importing joblib for saving and loading Python objects

# Load the dataset
data = pd.read_csv('data/fd_interest_rate_dataset.csv')  # Reading the dataset from a CSV file

# Separate features and target
X = data.drop('FD_Interest_Rate', axis=1)  # Dropping the target variable to create feature set
y = data['FD_Interest_Rate']  # Defining the target variable

# Define categorical and numerical features
categorical_features = ['Past_Transactions', 'Market_Trends']  # List of categorical feature names
numerical_features = ['Credit_History', 'Risk_Rating', 'Age', 'Customer_Relationship_Years']  # List of numerical feature names

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),  # Applying StandardScaler to numerical features
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)  # Applying OneHotEncoder to categorical features
    ]
)

# Build the pipeline/model
pipeline = Pipeline([
    ('preprocessor', preprocessor),  # Adding the preprocessor step to the pipeline
    ('model', RandomForestRegressor(n_estimators=100, random_state=42))  # Adding the RandomForestRegressor model to the pipeline
])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # Splitting the data into training and testing sets

# Fit or train the pipeline
pipeline.fit(X_train, y_train)  # Training the pipeline with the training data

# Save the entire pipeline
joblib.dump(pipeline, 'models/fd_model/fd_pipeline.pkl')  # Saving the trained pipeline to a file

print("Model training and pipeline saved successfully!")  # Printing a success message


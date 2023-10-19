# Python
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle

# Load the training data
data = pd.read_csv('ML/train.csv')

# Preprocessing
# Assuming the last column is the target variable
y = data.iloc[:, -1]
X = data.iloc[:, :-1]


# Standardize the features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Split the data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the model
gbrt = GradientBoostingRegressor(random_state=42)

# Define the grid of hyperparameters to search
param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.01, 0.1, 1],
    'max_depth': [1, 2, 3]
}

# Setup the grid search
grid_search = GridSearchCV(gbrt, param_grid, cv=5, scoring='neg_mean_squared_error')

# Fit the model and find optimal hyperparameters
grid_search.fit(X_train, y_train)

# Get the best model
best_gbrt = grid_search.best_estimator_

pickle.dump(best_gbrt, open('ML/model.pickle', "wb"))

# Predict on the validation set
y_pred = best_gbrt.predict(X_val)

#print(y_pred)

# Sort the validation set based on the predictions
sorted_indices = np.argsort(y_pred)

X_val_sorted = X_val[sorted_indices]

# Evaluate the model
mse = mean_squared_error(y_val, y_pred)
r2 = r2_score(y_val, y_pred)

print(mse)
print(r2)
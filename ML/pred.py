# Python
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle

model = pickle.load(open('ML/model.pickle', "rb"))

# Python
def predict(vehicles : list):
    
    if len(vehicles) == 0:
        return []
    
    # Convert the vehicles list to a numpy array
    df = pd.DataFrame(vehicles, columns=["numPassengers", "emissions", "distToTarget"])
    vehicles = df.iloc[:, :]

    scaler = StandardScaler()
    vehicles = scaler.fit_transform(vehicles) 

    # Predict the output
    predictions = model.predict(vehicles)

    # Sort the vehicles based on the predictions
    sorted_indices = np.argsort(predictions)

    return sorted_indices
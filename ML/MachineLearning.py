import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

# Load the training data
X_train = np.loadtxt('train_data.csv', delimiter=',')
y_train = np.loadtxt('train_labels.csv', delimiter=',')

# Train the GBRT model
model = GradientBoostingRegressor()
model.fit(X_train, y_train)

# Sort a new array
X_new = np.array([1, 2, 3])
y_pred = model.predict(X_new)

# The predicted ranking is y_pred
# Cash Assistance Eligibility Detection using SVM

## Overview
This project uses a **Support Vector Machine (SVM)** to classify whether a citizen is eligible for **cash assistance programs** based on demographic and socio-economic data.

## Features
- Input: Features like income, family size, employment status, housing, education  
- Output: Classification – `Eligible` or `Not Eligible`  
- Optimized SVM with kernel options (linear, RBF)

## Steps
1. **Data Collection**: Gather citizen data (survey, government records)  
2. **Preprocessing**: Handle missing data, encode categorical features, normalize numeric data  
3. **Model Training**: Train SVM classifier  
4. **Prediction & Evaluation**: Predict eligibility and evaluate with accuracy, precision, recall

## Python Example

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

# Load dataset
data = pd.read_csv("citizens_data.csv")

# Features and target
X = data.drop('eligible', axis=1)  # 'eligible' column = target
y = data['eligible']

# Encode categorical features if needed
X = pd.get_dummies(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train SVM
svm_model = SVC(kernel='rbf', C=1.0, gamma='scale')
svm_model.fit(X_train, y_train)

# Predictions
y_pred = svm_model.predict(X_test)

# Evaluate
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

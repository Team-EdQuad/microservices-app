# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
try:
    data = pd.read_csv("patterned_sample_data.csv")
except FileNotFoundError:
    print("Error: The file 'patterned_sample_data.csv' was not found.")
    exit()

# Drop constant columns if needed
if "Subject" in data.columns and "Class" in data.columns:
    data = data.drop(columns=["Subject", "Class"])

# Features & target
if "TotalActiveTime" not in data.columns:
    print("Error: 'TotalActiveTime' column is missing in the dataset.")
    exit()

X = data.drop("TotalActiveTime", axis=1)
y = data["TotalActiveTime"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_mse = mean_squared_error(y_test, lr_pred)
lr_rmse = lr_mse**0.5
lr_r2 = r2_score(y_test, lr_pred)

# Random Forest
rf = RandomForestRegressor(random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_rmse = rf_mse**0.5
rf_r2 = r2_score(y_test, rf_pred)

# XGBoost
xgb = XGBRegressor(random_state=42)
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)
xgb_mse = mean_squared_error(y_test, xgb_pred)
xgb_rmse = xgb_mse**0.5
xgb_r2 = r2_score(y_test, xgb_pred)

# Results
results = pd.DataFrame({
    "Model": ["Linear Regression", "Random Forest", "XGBoost"],
    "RMSE": [lr_rmse, rf_rmse, xgb_rmse],
    "R² Score": [lr_r2, rf_r2, xgb_r2]
})
print(results)

# Plot RMSE Comparison
sns.barplot(x="Model", y="RMSE", data=results)
plt.title("RMSE Comparison")
plt.show()

# Future Predictions
future = pd.DataFrame({
    "Weeknumber": [121, 122, 123],
    "SpecialEventThisWeek": [1, 0, 1],
    "ResourcesUploadedThisWeek": [3, 2, 4]
})

future_preds = lr.predict(future)
print(future_preds)

# Combine actual and predicted data
actual = data[["Weeknumber", "TotalActiveTime"]].copy()
actual["Type"] = "Actual"

predicted = future.copy()
predicted["TotalActiveTime"] = future_preds
predicted["Type"] = "Predicted"

combined = pd.concat([actual, predicted], ignore_index=True)
combined = combined.sort_values("Weeknumber")  # Sort by Weeknumber

# Plot Actual vs Predicted
plt.figure(figsize=(12, 6))
for label, df in combined.groupby("Type"):
    plt.plot(df["Weeknumber"], df["TotalActiveTime"], marker='o', label=label)



plt.xlabel("Week Number")
plt.ylabel("Total Active Time")
plt.title("Actual vs Predicted Total Active Time (Linear Regression)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
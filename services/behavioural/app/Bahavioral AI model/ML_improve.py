# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns

# Load dataset
try:
    data = pd.read_csv("patterned_sample_data.csv")
except FileNotFoundError:
    print("Error: The file 'patterned_sample_data.csv' was not found.")
    exit()

# Drop unwanted columns
data = data.drop(columns=["Subject", "Class"], errors="ignore")

# Features and target
if "TotalActiveTime" not in data.columns:
    print("Error: 'TotalActiveTime' column is missing in the dataset.")
    exit()

# Add lagged TotalActiveTime feature
data["TotalActiveTime_lag1"] = data["TotalActiveTime"].shift(1).fillna(0)

X = data.drop("TotalActiveTime", axis=1)
y = data["TotalActiveTime"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Original Linear Regression Model
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)

# Calculate original accuracy
original_mse = mean_squared_error(y_test, y_pred)
original_rmse = original_mse ** 0.5
original_r2 = r2_score(y_test, y_pred)

# Print test set predictions
print("\nTest Set Predictions (Original Model):")
for i in range(len(y_pred)):
    print(f"Input: {X_test.iloc[i].to_dict()} -> Predicted: {y_pred[i]:.2f}, Actual: {y_test.iloc[i]:.2f}")

print(f"\nOriginal Model Performance:\nRMSE: {original_rmse:.2f}\nR² Score: {original_r2:.2f}")

# Add predicted values to the dataset
test_predictions = X_test.copy()
test_predictions["TotalActiveTime"] = y_pred
test_predictions["Type"] = "Predicted (Test)"

# Combine original data and test predictions
actual_data = data.copy()
actual_data["Type"] = "Actual"
combined_data = pd.concat([actual_data, test_predictions], ignore_index=True)

# Recalculate lagged feature for combined dataset
combined_data = combined_data.sort_values("Weeknumber")
combined_data["TotalActiveTime_lag1"] = combined_data["TotalActiveTime"].shift(1).fillna(0)

# Retrain model on updated dataset
X_updated = combined_data.drop(["TotalActiveTime", "Type"], axis=1)
y_updated = combined_data["TotalActiveTime"]
lr_updated = LinearRegression()
lr_updated.fit(X_updated, y_updated)
y_pred_updated = lr_updated.predict(X_test)

# Calculate updated accuracy
updated_mse = mean_squared_error(y_test, y_pred_updated)
updated_rmse = updated_mse ** 0.5
updated_r2 = r2_score(y_test, y_pred_updated)

print(f"\nUpdated Model Performance (After Adding Predictions):\nRMSE: {updated_rmse:.2f}\nR² Score: {updated_r2:.2f}")

# Compare accuracies
results = pd.DataFrame({
    "Model": ["Original Linear Regression", "Updated Linear Regression"],
    "RMSE": [original_rmse, updated_rmse],
    "R² Score": [original_r2, updated_r2]
})
print("\nAccuracy Comparison:")
print(results)

# Plot RMSE comparison
plt.figure(figsize=(8, 5))
sns.barplot(x="Model", y="RMSE", hue="Model", data=results, palette="viridis", legend=False)
plt.title("RMSE Comparison: Original vs Updated Model (With Lagged Feature)")
plt.ylabel("RMSE")
plt.tight_layout()
plt.savefig("rmse_comparison_lagged.png")

# Future predictions for weeks 121, 122, 123 (iterative due to lagged feature)
future = pd.DataFrame({
    "Weeknumber": [121, 122, 123],
    "SpecialEventThisWeek": [1, 0, 1],
    "ResourcesUploadedThisWeek": [3, 2, 4],
    "TotalActiveTime_lag1": [data["TotalActiveTime"].iloc[-1]] + [None] * 2
})

future_preds = []
for i in range(len(future)):
    pred = lr_updated.predict(future.iloc[[i]])[0]
    future_preds.append(pred)
    if i < len(future) - 1:
        future.loc[i + 1, "TotalActiveTime_lag1"] = pred

# Combine data for visualization
future_predictions = future.copy()
future_predictions["TotalActiveTime"] = future_preds
future_predictions["Type"] = "Predicted (Future)"

combined_data = pd.concat([combined_data, future_predictions], ignore_index=True)
combined_data = combined_data.sort_values("Weeknumber")

# Plot Actual vs Predicted
plt.figure(figsize=(12, 6))
for label, df in combined_data.groupby("Type"):
    plt.plot(df["Weeknumber"], df["TotalActiveTime"], marker="o", label=label)

plt.xlabel("Week Number")
plt.ylabel("Total Active Time")
plt.title("Actual vs Predicted Total Active Time (With Lagged Feature)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("actual_vs_predicted_lagged.png")

# Print future predictions
print("\nFuture Predictions (Updated Model with Lagged Feature):")
for i, week in enumerate(future["Weeknumber"]):
    print(f"Week {week}: Predicted TotalActiveTime = {future_preds[i]:.2f}")
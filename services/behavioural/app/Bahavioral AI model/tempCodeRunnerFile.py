
for i in range(len(y_pred)):
    print(f"Input: {X_test.iloc[i].to_dict()} -> Predicted: {y_pred[i]}, Actual: {y_test.iloc[i]}")

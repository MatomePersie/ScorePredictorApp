# train_model.py
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load data
X, y = joblib.load("training_features.joblib")

# Train model
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=15,
    min_samples_split=5,
    random_state=42
)
model.fit(X, y)

# Evaluate (rough check)
pred = model.predict(X)
print("Training accuracy:", accuracy_score(y, pred))

joblib.dump(model, "model.joblib")
print("Model saved")

import pickle

# Load saved model
model = pickle.load(open("model.pkl", "rb"))

# Load vectorizer
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Test email
email = input("Enter email text: ")

# Convert text into numbers
email_vectorized = vectorizer.transform([email])

# Predict
prediction = model.predict(email_vectorized)

# Output result
print("Prediction:", prediction[0])
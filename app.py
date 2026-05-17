import streamlit as st
import pickle
from streamlit_oauth import OAuth2Component

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

# Load vectorizer
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ---------------- GOOGLE OAUTH ---------------- #

CLIENT_ID = "28501079710-iskm3ka55tf8617nk9jhpcpu2jr754ts.apps.googleusercontent.com"

CLIENT_SECRET = "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"

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"

TOKEN_URL = "https://oauth2.googleapis.com/token"

REDIRECT_URI = "https://smart-email-ai-clean.streamlit.app/component/streamlit_oauth.authorize_button/index.html"

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
)

# ---------------- STREAMLIT UI ---------------- #

st.title("Smart Email AI")

st.write("AI-Based Smart Email Classification System")

# ---------------- LOGIN BUTTON ---------------- #

result = oauth2.authorize_button(
    name="Login with Google",
    icon="https://www.google.com/favicon.ico",
    redirect_uri=REDIRECT_URI,
    scope="https://www.googleapis.com/auth/gmail.readonly",
    key="google",
)

# ---------------- EMAIL PREDICTION ---------------- #

def predict_email(text):

    text = text.lower()

    # Banking rules
    banking_keywords = [
        "credited",
        "debited",
        "transaction",
        "upi",
        "bank",
        "otp",
        "account"
    ]

    # Interview rules
    interview_keywords = [
        "interview",
        "assessment",
        "shortlisted",
        "coding round"
    ]

    # Job rules
    job_keywords = [
        "job",
        "hiring",
        "opportunity",
        "campus drive"
    ]

    # Recruiter rules
    recruiter_keywords = [
        "recruiter",
        "hr",
        "resume",
        "profile viewed"
    ]

    # Internship rules
    internship_keywords = [
        "internship",
        "intern"
    ]

    # Not important rules
    not_important_keywords = [
        "policy reminder",
        "newsletter",
        "google maps",
        "share their thoughts",
        "linkedin highlights",
        "offers",
        "discount",
        "sale"
    ]

    # Rule checking
    for word in banking_keywords:
        if word in text:
            return "BANKING"

    for word in interview_keywords:
        if word in text:
            return "INTERVIEW"

    for word in job_keywords:
        if word in text:
            return "JOB ALERT"

    for word in recruiter_keywords:
        if word in text:
            return "RECRUITER MESSAGE"

    for word in internship_keywords:
        if word in text:
            return "INTERNSHIP"

    for word in not_important_keywords:
        if word in text:
            return "NOT IMPORTANT"

    # ML prediction fallback
    text_vectorized = vectorizer.transform([text])

    prediction = model.predict(text_vectorized)

    return prediction[0]

# ---------------- AFTER LOGIN ---------------- #

if result and "token" in result:

    st.success("Google Login Successful")

    email_subject = st.text_input("Enter Email Subject")

    if st.button("Predict"):

        prediction = predict_email(email_subject)

        st.success(f"Prediction: {prediction}")

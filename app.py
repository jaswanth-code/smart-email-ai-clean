import streamlit as st
import pickle
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API permission
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

# Load vectorizer
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Streamlit UI
st.title("Smart Email AI")

st.write("AI-Based Smart Email Notification System")


# Predict email category
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

    # ML fallback
    text_vectorized = vectorizer.transform([text])

    prediction = model.predict(text_vectorized)

    return prediction[0]


# Gmail Login Function
def gmail_login():

    creds = None

    if os.path.exists('token.json'):

        creds = Credentials.from_authorized_user_file(
            'token.json',
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:

            token.write(creds.to_json())

    return creds


# Gmail Login Button
if st.button("Login With Gmail"):

    st.success("Gmail Authentication Started")

    creds = gmail_login()

    service = build('gmail', 'v1', credentials=creds)

    # Read Gmail
    results = service.users().messages().list(
        userId='me',
        q='category:primary OR category:updates',
        maxResults=10
    ).execute()

    messages = results.get('messages', [])

    st.subheader("Latest Email Predictions")

    # Process emails
    for message in messages:

        msg = service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()

        headers = msg['payload']['headers']

        subject = "No Subject"

        # Extract subject
        for header in headers:

            if header['name'] == 'Subject':

                subject = header['value']
        # Predict category
        prediction = predict_email(subject)

        # Display output
        if prediction == "NOT IMPORTANT":

            st.info(f"{prediction}: {subject}")

        else:

            st.success(f"{prediction}: {subject}")

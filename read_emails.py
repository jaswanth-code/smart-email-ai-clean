from winotify import Notification
import os.path
import pickle
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail read permission
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Number of emails to check
EMAIL_LIMIT = 20

# Important categories
IMPORTANT_CATEGORIES = [
    "INTERVIEW",
    "JOB ALERT",
    "INTERNSHIP",
    "RECRUITER MESSAGE",
    "BANKING"
]

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

# Load vectorizer
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))


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

    # Job alert rules
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
        "capstone challenge",
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


# Send Windows notification
def send_notification(title, message):

    # Unique notification ID
    unique_app_id = f"SmartEmailAI_{time.time()}"

    toast = Notification(
        app_id=unique_app_id,
        title=title,
        msg=message,
        duration="short"
    )

    toast.show()


def main():

    creds = None

    # Load saved token
    if os.path.exists('token.json'):

        creds = Credentials.from_authorized_user_file(
            'token.json',
            SCOPES
        )

    # Login again if token invalid
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save token
        with open('token.json', 'w') as token:

            token.write(creds.to_json())

    # Connect Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # Read only Primary + Updates emails
    results = service.users().messages().list(
        userId='me',
        q='category:primary OR category:updates',
        maxResults=EMAIL_LIMIT
    ).execute()

    messages = results.get('messages', [])

    print("\nLatest Emails:\n")

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
        result = predict_email(subject)

        # Print output
        print("Subject:", subject)
        print("Prediction:", result)
        print("-" * 50)

        # Send notification for important emails
        if result in IMPORTANT_CATEGORIES:

            print("Sending Notification...")

            send_notification(
                "Important Email Detected",
                f"{result}: {subject}"
            )

            # Delay between notifications
            time.sleep(3)


if __name__ == '__main__':
    main()
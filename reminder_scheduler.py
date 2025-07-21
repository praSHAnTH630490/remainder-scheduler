import schedule
import smtplib
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["trackmybill"]
bills_collection = db["bills"]

# Function to send reminder email
def send_email(to_email, subject, body):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, APP_PASSWORD)
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL
            msg['To'] = to_email
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print(f"✅ Sent reminder to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Function to check and send reminders
def check_and_send_reminders():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    start = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    end = start + timedelta(days=1)

    query = {
        "reminder": True,
        "status": "Unpaid",
        "due_date": {"$gte": start, "$lt": end}
    }

    print(f"📬 Checking for reminders on {now.strftime('%Y-%m-%d %H:%M')}...")
    reminders = bills_collection.find(query)

    for bill in reminders:
        to_email = bill.get("email")
        label = bill.get("description", "a bill")
        due_date = bill.get("due_date").strftime("%Y-%m-%d")
        amount = bill.get("amount", "N/A")
        subject = f"Reminder: Your bill for {label} is due tomorrow!"
        body = (
            f"Hello,\n\nThis is a reminder that your bill for '{label}' "
            f"amounting to ₹{amount} is due on {due_date}.\n\nPlease ensure timely payment.\n\nTrackMyBill"
        )
        send_email(to_email, subject, body)

# Schedule the task to run every day at 9:00 AM
schedule.every().day.at("09:00").do(check_and_send_reminders)

def start_scheduler():
    print("📅 Scheduler running daily at 9:00 AM...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    check_and_send_reminders() 

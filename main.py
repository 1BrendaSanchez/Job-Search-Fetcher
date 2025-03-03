import requests
import smtplib
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
JOB_TITLE = "Cloud Security Engineer"
LOCATION = "Remote"
INDEED_API_KEY = "YOUR_API_KEY"  # Use API if available
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_password"
EMAIL_RECEIVER = "your_email@gmail.com"


def get_jobs_from_indeed():
    """Fetch job postings from Indeed API"""
    url = "https://api.indeed.com/v2/jobs"
    params = {"q": JOB_TITLE, "l": LOCATION, "api_key": INDEED_API_KEY}
    response = requests.get(url, params=params)
    return response.json().get("results", [])


def scrape_jobs_from_linkedin():
    """Scrape job postings from LinkedIn (if no API available)"""
    url = f"https://www.linkedin.com/jobs/search/?keywords={JOB_TITLE.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for job in soup.find_all("div", class_="job-result-card"):
        title = job.find("h3").text.strip()
        company = job.find("h4").text.strip()
        link = job.find("a")["href"]
        jobs.append({"title": title, "company": company, "link": link})

    return jobs


def send_email(subject, body):
    """Send job notifications via email"""
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)


def send_telegram_message(message):
    """Send job notifications via Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)


def main():
    """Main function to get jobs and send notifications"""
    jobs = get_jobs_from_indeed() if INDEED_API_KEY else scrape_jobs_from_linkedin()

    if not jobs:
        print("No new jobs found.")
        return

    job_messages = []
    for job in jobs[:5]:  # Limit to top 5 results
        job_text = f"{job['title']} at {job['company']}\n{job.get('link', 'No link available')}"
        job_messages.append(job_text)

    message_body = "\n\n".join(job_messages)
    send_email("New Job Alert", message_body)
    send_telegram_message(message_body)

    print("Job alerts sent!")


if __name__ == "__main__":
    main()

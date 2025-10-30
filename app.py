import os
import base64
import requests
from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔹 Brevo API key from environment variable
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apply", methods=["POST"])
def apply():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        cover = request.form.get("cover")
        job_id = request.form.get("jobId")
        resume = request.files.get("resume")

        if not resume:
            return "❌ Please upload your resume!"

        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        subject = f"New Job Application — {name}"
        body = f"""
New Job Application Received

🧾 Job ID: {job_id}
👤 Name: {name}
📧 Email: {email}
📞 Phone: {phone}

💬 Cover Letter:
{cover}
"""

        # ✅ Brevo API endpoint
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": os.getenv("BREVO_API_KEY"),
        }

        files = {
            "attachment": (resume.filename, open(filepath, "rb"), "application/octet-stream")
        }

        data = {
            "sender": {"email": "mogappairgtec@gmail.com"},
            "to": [{"email": "mogappairgtec@gmail.com"}],
            "subject": subject,
            "textContent": body
        }

        print("📡 Sending email through Brevo API...")
        response = requests.post(url, headers=headers, data=data, files=files, timeout=20)

        if response.status_code == 201:
            print("✅ Email sent successfully via Brevo API!")
            return "✅ Application sent successfully!"
        else:
            print("❌ Error:", response.text)
            return f"❌ Failed to send email: {response.text}"

    except Exception as e:
        print("❌ Exception:", e)
        return f"❌ Error sending application: {e}"

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

import os
import base64
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔹 Environment variables
EMAIL_USER = os.getenv("EMAIL_USER")  # Brevo sender email (must be verified)
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Brevo API key
HR_EMAIL = os.getenv("HR_EMAIL", EMAIL_USER)  # Default to sender if not set

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apply", methods=["POST"])
def apply():
    try:
        # 🔹 Get form fields
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        cover = request.form.get("cover")
        job_id = request.form.get("jobId")
        resume = request.files.get("resume")

        # 🔹 Validation
        if not all([name, email, phone, resume]):
            return jsonify({"status": "error", "message": "❌ Please fill all required fields!"}), 400

        # 🔹 Save uploaded file temporarily
        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        # 🔹 Convert file to Base64 for Brevo attachment
        with open(filepath, "rb") as f:
            file_data = base64.b64encode(f.read()).decode()

        # 🔹 Brevo API setup
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": EMAIL_PASS,
            "content-type": "application/json",
        }

        # 🔹 Email content to HR
        data = {
            "sender": {"name": "Job Application Portal", "email": EMAIL_USER},
            "to": [{"email": HR_EMAIL}],  # ✅ Sends to HR email (or sender if HR_EMAIL missing)
            "subject": f"New Job Application — {name}",
            "htmlContent": f"""
                <h3>New Job Application Received</h3>
                <p><b>Job ID:</b> {job_id or "N/A"}</p>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Cover Letter:</b><br>{cover or "Not provided"}</p>
            """,
            "attachment": [
                {
                    "name": resume.filename,
                    "content": file_data
                }
            ]
        }

        # 🔹 Send email to HR
        response = requests.post(url, headers=headers, json=data)
        os.remove(filepath)

        if response.status_code not in [200, 201]:
            print("❌ Brevo API Error:", response.text)
            return jsonify({"status": "error", "message": "❌ Failed to send email via Brevo API."}), 500

        print("✅ Email with attachment sent successfully!")

        # 🔹 Optional: Send confirmation email to applicant
        confirm_data = {
            "sender": {"name": "Aura Institute HR", "email": EMAIL_USER},
            "to": [{"email": email}],
            "subject": "Thank you for applying!",
            "htmlContent": f"""
                <p>Dear {name},</p>
                <p>Thank you for applying for the position at <b>Aura Institute & Technology</b>.</p>
                <p>Our HR team will review your application and contact you shortly.</p>
                <br>
                <p>Best regards,<br>Aura HR Team</p>
            """
        }

        requests.post(url, headers=headers, json=confirm_data)

        return jsonify({"status": "success", "message": "✅ Application sent successfully!"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

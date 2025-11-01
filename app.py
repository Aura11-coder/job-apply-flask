import os
import base64
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMAIL_USER = os.getenv("EMAIL_USER")  # Brevo sender email
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Brevo API key

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
            return jsonify({"status": "error", "message": "❌ Please upload your resume!"}), 400

        # Save file temporarily
        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        # Convert file to base64
        with open(filepath, "rb") as f:
            file_data = base64.b64encode(f.read()).decode()

        # Prepare Brevo API request
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": EMAIL_PASS,
            "content-type": "application/json",
        }

        data = {
            "sender": {"name": "Job Application Portal", "email": EMAIL_USER},
            "to": [{"email": EMAIL_USER}],
            "subject": f"New Job Application — {name}",
            "htmlContent": f"""
                <h3>New Job Application Received</h3>
                <p><b>Job ID:</b> {job_id}</p>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Cover Letter:</b><br>{cover}</p>
            """,
            "attachment": [
                {
                    "name": resume.filename,
                    "content": file_data
                }
            ]
        }

        # Send email via Brevo API
        response = requests.post(url, headers=headers, json=data)
        os.remove(filepath)

        if response.status_code in [200, 201]:
            print("✅ Email with attachment sent successfully!")
            return jsonify({"status": "success", "message": "✅ Application sent successfully!"})
        else:
            print("❌ Brevo API Error:", response.text)
            return jsonify({"status": "error", "message": "❌ Failed to send email via Brevo API."}), 500

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

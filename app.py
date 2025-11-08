import os
import base64
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
HR_EMAIL = os.getenv("HR_EMAIL", EMAIL_USER)

app = Flask(__name__)
CORS(app)

# 🔹 Dummy job data
jobs = [
    {"id": 1, "title": "Data Engineer", "company": "None", "location": "Bangalore/Puna/Kolkata/Hyderabad", "eligible": "Any degree/Python or Scala / SQL,and data pipeline","experience":"1.5 to 3.5"},

    {"id": 2, "title": "Analyst - Accounts Payable", "company": "flex", "location": "Chennai", "eligible": "B.com/BBA/M.com/MBA","experience":"Freshers"},
    {"id": 3, "title": "Python Developer", "company": "rccenterprises", "location": "Perungudi", "eligible": "Creating the back-end elements/python","experience":"Freshers"},
    {"id": 4, "title": "Accountant Lady", "company": "Headphonezone pvt ltd", "location": "Chennai", "eligible": "Tally Prime/Excel/Google Sheets","experience":"Freshers"},
    {"id": 5, "title": "Senior Analyst-procurement", "company": "FLEX", "location": "Chennai", "eligible": "Good Communication& SAP","experience":"1-2 Years"},
    {"id": 6, "title": "Accountant and Office Administration", "company": "Sambavi Meditek", "location": "Medavakkam", "eligible": "Tally Prime with GST","experience":"2 years experience "},
    {"id": 7, "title": "Java Developer", "company": "Hyeongshin Automotive Industry", "location": "Chennai", "eligible": "java ,Spring framework, Spring Boot,REST","experience":"Freshers"}
    


]

@app.route("/")
def job_list():
    return render_template("jobs.html", jobs=jobs)

@app.route("/application/<int:job_id>")
def application(job_id):
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        return "Job not found", 404
    return render_template("apply.html", job=job)

@app.route("/apply", methods=["POST"])
def apply():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        cover = request.form.get("cover")
        job_id = request.form.get("jobId")
        resume = request.files.get("resume")

        if not all([name, email, phone, resume]):
            return jsonify({"status": "error", "message": "❌ Please fill all required fields!"}), 400

        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        with open(filepath, "rb") as f:
            file_data = base64.b64encode(f.read()).decode()

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json",
        }

        data = {
            "sender": {"name": "Job Application Portal", "email": EMAIL_USER},
            "to": [{"email": HR_EMAIL}],
            "subject": f"New Job Application — {name}",
            "htmlContent": f"""
                <h3>New Job Application Received</h3>
                <p><b>Job ID:</b> {job_id or "N/A"}</p>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Cover Letter:</b><br>{cover or "Not provided"}</p>
            """,
            "attachment": [{"name": resume.filename, "content": file_data}]
        }

        response = requests.post(url, headers=headers, json=data)
        os.remove(filepath)

        if response.status_code not in [200, 201]:
            print("❌ Brevo API Error:", response.text)
            return jsonify({"status": "error", "message": "❌ Failed to send email via Brevo API."}), 500

        # Send confirmation email to applicant
        confirm_data = {
            "sender": {"name": "ZobsZoom HR", "email": EMAIL_USER},
            "to": [{"email": email}],
            "subject": "Thank you for applying!",
            "htmlContent": f"""
                <p>Dear {name},</p>
                <p>Thank you for applying for the position at <b>ZobsZoom</b>.</p>
                <p>Our HR team will review your application and contact you shortly.</p>
                <br><p>Best regards,<br>ZobsZoom HR Team</p>
            """
        }
        requests.post(url, headers=headers, json=confirm_data)

        return jsonify({"status": "success", "message": "✅ Application sent successfully!"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

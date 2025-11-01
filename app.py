import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

# 🔹 Set your environment variables in Render Dashboard
EMAIL_USER = os.getenv("EMAIL_USER")  # your Brevo login email
EMAIL_PASS = os.getenv("EMAIL_PASS")  # your Brevo SMTP key

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

        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        msg = EmailMessage()
        msg["Subject"] = f"New Job Application — {name}"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER

        msg.set_content(f"""
New Job Application Received:

🧾 Job ID: {job_id}
👤 Name: {name}
📧 Email: {email}
📞 Phone: {phone}

💬 Cover Letter:
{cover}
""")

        # Attach the resume file
        with open(filepath, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=resume.filename)

        # 🔹 Brevo SMTP
        with smtplib.SMTP("smtp-relay.brevo.com", 587, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        os.remove(filepath)
        print("✅ Email sent successfully!")
        return jsonify({"status": "success", "message": "✅ Application sent successfully!"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

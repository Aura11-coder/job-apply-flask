import os
from flask import Flask, render_template, request
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

# 🔹 Gmail credentials from Render environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


@app.route("/")
def home():
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

        # 🔹 Save uploaded resume to /tmp before attaching
        filepath = None
        if resume:
            filename = resume.filename
            filepath = os.path.join("/tmp", filename)
            resume.save(filepath)

        # 🔹 Create email
        msg = EmailMessage()
        msg["Subject"] = f"New Job Application — {name}"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_USER

        msg.set_content(f"""
New Job Application Received

🧾 Job ID: {job_id}
👤 Name: {name}
📧 Email: {email}
📞 Phone: {phone}

💬 Cover Letter:
{cover}
""")

        # 🔹 Attach the saved resume file (if available)
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(filepath)
                )

        # 🔹 Send mail via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        return "✅ Application sent successfully! Check your email."

    except Exception as e:
        print("Email send error:", e)
        return f"❌ Error sending email: {e}"


if __name__ == "__main__":
    app.run(debug=True)

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

        with open(filepath, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=resume.filename
            )

        print("🔹 Connecting to Brevo SMTP server...")
        with smtplib.SMTP("smtp-relay.brevo.com", 587, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("✅ Email sent successfully!")
        os.remove(filepath)
        return "✅ Application sent successfully! Check your email."

    except Exception as e:   # 👈 this closes the try properly
        print("❌ Error:", e)
        return f"❌ Error sending application: {e}"


if __name__ == "__main__":
    app.run(debug=True)

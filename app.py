from flask import Flask, render_template, request
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

# 🔹 Replace these with your Gmail credentials
YOUR_EMAIL = "mogappairgtec@gmail.com"
YOUR_APP_PASSWORD = "henk yigv krhx mpxz"  # from https://myaccount.google.com/apppasswords


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/apply", methods=["POST"])
def apply():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    cover = request.form.get("cover")
    job_id = request.form.get("jobId")
    resume = request.files["resume"]

    msg = EmailMessage()
    msg["Subject"] = f"New Job Application — {name}"
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL

    msg.set_content(f"""
New Job Application Received

🧾 Job ID: {job_id}
👤 Name: {name}
📧 Email: {email}
📞 Phone: {phone}

💬 Cover Letter:
{cover}
""")

    if resume:
        msg.add_attachment(
            resume.read(),
            maintype="application",
            subtype="pdf",
            filename=resume.filename
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            smtp.send_message(msg)
        return "✅ Application sent successfully! Check your email."
    except Exception as e:
        print("Email send error:", e)
        return f"❌ Error sending email: {e}"


if __name__ == "__main__":
    app.run(debug=True)

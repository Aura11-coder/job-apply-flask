import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- SMTP CONFIG (Brevo) ---
app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '9a5a04001@smtp-brevo.com'  # Brevo login
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")      # Brevo SMTP key
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# HR email address (to receive applications)
HR_EMAIL = os.getenv("HR_EMAIL", "mogappairgtec@gmail.com")


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

        # Save resume temporarily
        filepath = os.path.join("/tmp", resume.filename)
        resume.save(filepath)

        # --- Compose Email ---
        msg = Message(
            subject=f"New Job Application — {name}",
            sender=("Job Application Portal", app.config['MAIL_USERNAME']),
            recipients=[HR_EMAIL]
        )

        msg.html = f"""
        <h3>New Job Application Received</h3>
        <p><b>Job ID:</b> {job_id}</p>
        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Cover Letter:</b><br>{cover}</p>
        """

        # --- Attach Resume ---
        with open(filepath, "rb") as fp:
            msg.attach(resume.filename, "application/octet-stream", fp.read())

        # --- Send Email ---
        mail.send(msg)
        os.remove(filepath)

        print("✅ Email sent successfully via SMTP!")
        return jsonify({"status": "success", "message": "✅ Application sent successfully!"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 🔹 Formspree endpoint
FORMSPREE_URL = "https://formspree.io/f/mkgppqpv"

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

        # Prepare form data for Formspree
        with open(filepath, "rb") as f:
            files = {"resume": (resume.filename, f, "application/octet-stream")}
            data = {
                "Job ID": job_id,
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Cover Letter": cover,
            }

            # 🔹 Send to Formspree
            response = requests.post(FORMSPREE_URL, data=data, files=files)

        os.remove(filepath)

        if response.status_code == 200:
            return jsonify({"status": "success", "message": "✅ Application sent successfully!"})
        else:
            return jsonify({"status": "error", "message": f"❌ Failed to send application. ({response.status_code})"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": f"❌ Error sending application: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

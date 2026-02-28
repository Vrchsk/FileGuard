import os
import hashlib
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
HASH_FILE = "hash_store.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        file = request.files["file"]
        action = request.form["action"]

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        file_hash = generate_hash(file_path)

        if action == "store":
            with open(HASH_FILE, "a") as f:
                f.write(f"{file.filename}:{file_hash}\n")
            message = f"Hash stored successfully for {file.filename}"

        elif action == "verify":
            stored_hash = None
            if os.path.exists(HASH_FILE):
                with open(HASH_FILE, "r") as f:
                    for line in f:
                        name, hash_val = line.strip().split(":")
                        if name == file.filename:
                            stored_hash = hash_val
                            break

            if stored_hash == file_hash:
                message = "Integrity Check PASSED: File is unchanged"
            else:
                message = "Integrity Check FAILED: File may be tampered"

    return render_template("home.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)

app.secret_key = "zero-trust-demo-key"


# Demo users
users = {
    "nasrath": {
        "password": "1234",
        "role": "Employee"
    },
    "admin": {
        "password": "admin123",
        "role": "Admin"
    }
}


# ---------------- ACCESS LOGGING ----------------

def log_access(username, role, resource, decision):

    with open("access.log", "a") as log_file:

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_file.write(
            f"{time} | User: {username} | "
            f"Role: {role} | Resource: {resource} | "
            f"Decision: {decision}\n"
        )


# ---------------- LOGIN / IDENTITY CHECK ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:

            session["username"] = username
            session["role"] = users[username]["role"]

            return render_template("device.html")

        else:

            message = "Identity verification failed. Access denied."

    return render_template("login.html", message=message)


# ---------------- DEVICE TRUST CHECK ----------------

@app.route("/device", methods=["GET", "POST"])
def device_check():

    message = ""

    if request.method == "POST":

        device_status = request.form["device_status"]

        if device_status == "trusted":

            session["device_trusted"] = True

            return render_template("resource.html")

        else:

            session["device_trusted"] = False

            message = "Device verification failed. Device is untrusted."

    return render_template("device.html", message=message)


# ---------------- RESOURCE ACCESS CHECK ----------------

@app.route("/resource", methods=["GET", "POST"])
def resource_access():

    message = ""

    username = session.get("username")
    role = session.get("role")
    device_trusted = session.get("device_trusted", False)

    if not username or not device_trusted:

        message = "Access denied. Identity or device verification failed."

        return render_template("resource.html", message=message)

    if request.method == "POST":

        resource = request.form["resource"]

        if resource == "internal" and role in ["Employee", "Admin"]:

            message = "Access granted. You can access Internal Documents."

            log_access(username, role, resource, "ALLOWED")

        elif resource == "admin" and role == "Admin":

            message = "Access granted. You can access the Admin Panel."

            log_access(username, role, resource, "ALLOWED")

        elif resource == "public":

            message = "Access granted. You can access Public Information."

            log_access(username, role, resource, "ALLOWED")

        else:

            message = "Access denied. Your role does not have permission."

            log_access(username, role, resource, "DENIED")

    return render_template("resource.html", message=message)


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)

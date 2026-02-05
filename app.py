from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DATA_DIR = "data"
USERS_FILE = "users.json"

os.makedirs(DATA_DIR, exist_ok=True)


# ---------- USERS ----------

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# ---------- NOTES ----------

def get_user_file():
    user = session.get("user")
    if not user:
        return None
    return os.path.join(DATA_DIR, f"{user}.json")


def load_notes():
    user_file = get_user_file()
    if not user_file or not os.path.exists(user_file):
        return []

    try:
        with open(user_file, "r", encoding="utf-8") as f:
            notes = json.load(f)
    except json.JSONDecodeError:
        return []

    changed = False
    for note in notes:
        if "created_at" not in note:
            note["created_at"] = datetime.now().isoformat()
            changed = True
        if "pinned" not in note:
            note["pinned"] = False
            changed = True

    if changed:
        save_notes(notes)

    return notes


def save_notes(notes):
    user_file = get_user_file()
    if not user_file:
        return
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def get_next_id(notes):
    return max([n["id"] for n in notes], default=0) + 1


# ---------- AUTH ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_users()

    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")

        if username in users:
            return render_template("register.html", error="Korisnik već postoji")

        users[username] = generate_password_hash(password)
        save_users(users)

        session["user"] = username
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    users = load_users()

    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect(url_for("index"))

        return render_template("login.html", error="Pogrešni podaci")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------- NOTES ROUTES ----------

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    notes = load_notes()

    if request.method == "POST":
        text = request.form.get("text")
        if text:
            notes.append({
                "id": get_next_id(notes),
                "text": text,
                "created_at": datetime.now().isoformat(),
                "pinned": False
            })
            save_notes(notes)
        return redirect(url_for("index"))

    pinned = [n for n in notes if n["pinned"]]
    normal = [n for n in notes if not n["pinned"]]

    pinned.sort(key=lambda n: n["id"], reverse=True)
    normal.sort(key=lambda n: n["id"], reverse=True)

    return render_template(
        "index.html",
        notes=pinned + normal,
        user=session["user"]
    )


@app.route("/toggle_pin/<int:note_id>", methods=["POST"])
def toggle_pin(note_id):
    notes = load_notes()
    note = next((n for n in notes if n["id"] == note_id), None)
    if note:
        note["pinned"] = not note["pinned"]
        save_notes(notes)
    return redirect(url_for("index"))


@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit(note_id):
    notes = load_notes()
    note = next((n for n in notes if n["id"] == note_id), None)

    if not note:
        return redirect(url_for("index"))

    if request.method == "POST":
        note["text"] = request.form.get("text")
        save_notes(notes)
        return redirect(url_for("index"))

    return render_template("edit.html", note=note)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    notes = load_notes()
    notes = [n for n in notes if n["id"] != note_id]
    save_notes(notes)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

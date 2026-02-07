from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# ---------- ROUTES ----------

@app.route("/login")
def login():
    # Supabase auth se radi u browseru (JS)
    return render_template("login.html")


@app.route("/logout")
def logout():
    # Logout se radi u Supabase JS
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    # NOTE:
    # Auth i user dolaze iz Supabase-a (frontend)
    # Za sada Flask samo renderuje stranicu

    notes = []  # privremeno prazno, DB dolazi u sljedećem koraku

    return render_template(
        "index.html",
        notes=notes,
        user=None
    )


@app.route("/edit/<int:note_id>")
def edit(note_id):
    return redirect(url_for("index"))


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    return redirect(url_for("index"))


@app.route("/toggle_pin/<int:note_id>", methods=["POST"])
def toggle_pin(note_id):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

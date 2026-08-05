"""
Book Manager — Flask + Jinja + SQLite + Bootstrap + Chart.js + Three.js

Single-file backend. Routes, DB helpers, and analytics queries all live
here for MVP simplicity (no blueprints/services layer).
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, g, render_template, request, redirect, url_for, abort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "storage", "db.sqlite")

app = Flask(__name__)

# Fixed category list -> keeps the dashboard charts meaningful (free-text
# categories would fragment into dozens of one-off slices).
CATEGORIES = [
    "Fiction", "Non-Fiction", "Science", "Technology",
    "Biography", "History", "Fantasy", "Self-Help", "Other",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    author      TEXT NOT NULL,
    price       REAL NOT NULL,
    category    TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_books_category ON books (category);
"""


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        os.makedirs(os.path.join(BASE_DIR, "storage"), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "storage"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def validate_book_form(form):
    """Shared validation for add + edit. Returns (cleaned_data, errors)."""
    name = form.get("name", "").strip()
    author = form.get("author", "").strip()
    category = form.get("category", "").strip()
    price_raw = form.get("price", "").strip()

    errors = []
    if not name:
        errors.append("Book name cannot be empty.")
    if not author:
        errors.append("Author cannot be empty.")
    if category not in CATEGORIES:
        errors.append("Please choose a valid category.")

    price = None
    if not price_raw:
        errors.append("Price cannot be empty.")
    else:
        try:
            price = float(price_raw)
            if price <= 0:
                errors.append("Price must be a positive number.")
        except ValueError:
            errors.append("Price must be a valid number.")

    return {"name": name, "author": author, "category": category, "price": price_raw}, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    db = get_db()
    books = db.execute("SELECT * FROM books ORDER BY created_at DESC").fetchall()
    return render_template("home.html", books=books)


@app.route("/books/add/", methods=["GET", "POST"])
def add_books():
    if request.method == "POST":
        cleaned, errors = validate_book_form(request.form)
        if errors:
            return render_template("add_books.html", categories=CATEGORIES,
                                    book=cleaned, errors=errors)

        db = get_db()
        db.execute(
            "INSERT INTO books (name, author, price, category) VALUES (?, ?, ?, ?)",
            (cleaned["name"], cleaned["author"], float(cleaned["price"]), cleaned["category"]),
        )
        db.commit()
        return redirect(url_for("home"))

    return render_template("add_books.html", categories=CATEGORIES, book=None, errors=[])


@app.route("/books/<int:book_id>/")
def book_details(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)
    return render_template("details.html", book=book)


@app.route("/books/edit/<int:book_id>/", methods=["GET", "POST"])
def edit_books(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)

    if request.method == "POST":
        cleaned, errors = validate_book_form(request.form)
        if errors:
            cleaned["id"] = book_id
            return render_template("edit_book.html", categories=CATEGORIES,
                                    book=cleaned, errors=errors)

        db.execute(
            "UPDATE books SET name = ?, author = ?, price = ?, category = ? WHERE id = ?",
            (cleaned["name"], cleaned["author"], float(cleaned["price"]), cleaned["category"], book_id),
        )
        db.commit()
        return redirect(url_for("book_details", book_id=book_id))

    return render_template("edit_book.html", categories=CATEGORIES, book=book, errors=[])


@app.route("/books/delete/<int:book_id>/", methods=["POST"])
def delete_books(book_id):
    db = get_db()
    book = db.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return redirect(url_for("home"))


@app.route("/books/dashboard/")
def dashboard():
    db = get_db()

    total_books = db.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    total_value = db.execute("SELECT COALESCE(SUM(price), 0) AS v FROM books").fetchone()["v"]
    avg_price = db.execute("SELECT COALESCE(AVG(price), 0) AS a FROM books").fetchone()["a"]

    by_category = db.execute(
        "SELECT category, COUNT(*) AS count, COALESCE(SUM(price),0) AS value "
        "FROM books GROUP BY category ORDER BY count DESC"
    ).fetchall()

    category_labels = [row["category"] for row in by_category]
    category_counts = [row["count"] for row in by_category]
    category_values = [round(row["value"], 2) for row in by_category]

    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_value=round(total_value, 2),
        avg_price=round(avg_price, 2),
        category_labels=category_labels,
        category_counts=category_counts,
        category_values=category_values,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
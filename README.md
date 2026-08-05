# 📚 Book Management

A simple book inventory manager built with Flask, SQLite, and Bootstrap — with a small analytics dashboard powered by Chart.js and a decorative Three.js animation.

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (`storage/db.sqlite`, created automatically on first run)
- **Frontend:** Jinja templates + Bootstrap 5
- **Charts:** Chart.js (bar + doughnut charts on the dashboard)
- **3D animation:** Three.js (small decorative rotating cube on the dashboard)

## Project Structure

```
book-management/
├── app.py                    # Flask app: routes, DB logic, validation
├── static/
│   └── style.css             # Design system (colors, fonts, navbar, animations)
├── storage/
│   └── db.sqlite             # SQLite database (auto-created, don't commit this)
└── templates/
    ├── home.html              # Book list (view/edit/delete, add book link)
    ├── add_books.html         # Add book form
    ├── edit_books.html        # Edit book form
    ├── details.html           # Single book detail view
    └── dashboard.html         # Analytics: totals + charts
```

## Features

- Full CRUD on books: add, view, edit, delete
- Fields: name, author, price, category (fixed dropdown list)
- Validation: no empty name/author, category must be valid, price must be a positive number
- Dashboard: total books, total inventory value, average price, plus category breakdown charts

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | List all books |
| GET/POST | `/books/add/` | Add a new book |
| GET | `/books/<id>/` | View a single book's details |
| GET/POST | `/books/edit/<id>/` | Edit a book |
| POST | `/books/delete/<id>/` | Delete a book |
| GET | `/books/dashboard/` | Analytics dashboard |

## Setup & Running Locally

**1. Install Flask**
```bash
pip install flask
```

**2. Run the app** (from the folder containing `app.py`)
```bash
python app.py
```

**3. Open in your browser**
```
http://127.0.0.1:5000
```

The SQLite database is created automatically the first time the app runs — no manual setup needed.

## Notes

- Make sure `static/`, `storage/`, and `templates/` all sit at the same folder level as `app.py` (siblings, not nested inside each other) — Flask looks for them relative to the project root.
- `storage/db.sqlite` is regenerated automatically, so it's safe to exclude from version control (see `.gitignore` below).

## Suggested `.gitignore`

```
storage/db.sqlite
__pycache__/
*.pyc
```

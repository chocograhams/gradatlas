
# GradAtlas Flask App

GradAtlas is a one-page web application built with Flask that allows graduate students and organizers to:

- Search for academic and social meetups by tag, location, name, or description
- Select events of interest using checkboxes
- Export selected events into a downloadable CSV or JSON file
- Manage events using a browser-based admin panel with PostgreSQL

---

## Features

- Responsive one-page layout
- Search filters by tag, location, name, or event description
- Real-time display of matching results
- Export selected meetups to CSV or JSON
- Admin panel for adding/editing events (protected login)
- PostgreSQL-compatible for deployment

---

## Requirements

- Python 3.x ([Download Python](https://www.python.org/downloads/))
- pip (comes with Python)
- Web browser (Chrome, Firefox, Safari, etc.)

---

## Option 1: Local Installation

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/your-username/gradatlas.git
cd gradatlas
```

### Step 2: Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variable (Optional for PostgreSQL)

```bash
export DATABASE_URL=sqlite:///meetups.db
```

### Step 5: Run the App

```bash
python meetup_api3.py
```

Then visit [http://127.0.0.1:5002/search](http://127.0.0.1:5002/search)

---

## Option 2: Deploy to Render

1. Push your code to GitHub (including `meetup_api3.py`, `templates/`, `static/`, and `requirements.txt`)
2. Go to [https://render.com](https://render.com) and click "New Web Service"
3. Link your GitHub repo and set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn meetup_api3:app`
4. Under **Advanced Settings**:
   - Add environment variable `DATABASE_URL` pointing to your PostgreSQL database
5. Click **Deploy**

After deployment, visit `/search` to use the app, or `/admin` after logging in via `/login`.

---

## Login Info for Admin

Go to `/login` and enter:

- Username: `admin`
- Password: `password123`

---

## Project Structure

```
gradatlas/
├── meetup_api3.py
├── requirements.txt
├── templates/
│   └── search_meetups_with_export_logo_welcome.html
├── static/
│   └── Gradatlas_logo3.png
```

---

## Credits

Created by Christine Chen and Yue Liu. Designed for student communities to manage and discover events easily.

---

## Need Help?

Reach out or open an issue. Enjoy using GradAtlas!

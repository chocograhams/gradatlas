# 🎓 GradAtlas Flask App

GradAtlas is a one-page web application built with Flask that allows graduate students and organizers to:

- 🔍 Search for academic and social meetups by tag, location, name, or description
- ✅ Select events of interest using checkboxes
- 📥 Export selected events into a downloadable CSV file

This is perfect for institutions or student communities that want a lightweight, local event discovery and export tool.

---

## 🚀 Features

- Responsive one-page layout
- GradAtlas branding with custom logo
- Search filters by tag, location, name, or event description
- Real-time display of matching results
- Checkbox selection for exporting meetups to CSV
- Welcome message and logo integrated in header

---

## 🧰 Requirements

- Python 3.x installed ([Download Python](https://www.python.org/downloads/))
- pip (usually comes with Python)
- Web browser (Chrome, Firefox, Safari, etc.)

---

## 📦 Setup Instructions (Option 1: Local Installation)

### Step 1: Clone or Download the Project

Unzip the provided `GradAtlas_FlaskApp.zip` into a local directory.

Alternatively, if using Git:

```bash
git clone https://your-github-url/GradAtlas_FlaskApp.git
cd GradAtlas_FlaskApp
```

### Step 2: Set Up a Python Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Step 3: Install Flask and Dependencies

```bash
pip install flask flask-cors
```

### Step 4: Run the Flask Server

```bash
python meetup_api3.py
```

If successful, your terminal will say:

```
Running on http://127.0.0.1:5002/
```

---

## 🌐 Usage Instructions

### Visit the Search Page

Open your browser and go to:

```
http://127.0.0.1:5002/search
```

### On the Web Page You Can:

1. Choose a filter (e.g., Tag, Location)
2. Enter a keyword like "social" or "Seattle"
3. See matching meetups
4. ✅ Select the ones you want to export
5. Click **"Download Selected as CSV"** to save them to your computer

---

## 📁 Project Structure

```
GradAtlas_FlaskApp/
├── meetup_api3.py                      # Flask app with all routes
├── meetups-list.json                  # Sample event data
├── README.md                          # This guide
├── templates/
│   └── search_meetups_with_export_logo_welcome.html
├── static/
│   └── Gradatlas_logo3.png            # Logo used in header
```

---

## 🤝 Credits

Created by Christine Chen and Yue Liu. Designed for academic and student communities interested in event sharing and search tools.

---

## 🛠 Optional Improvements

- Add date or time filtering
- Add login or admin panel
- Deploy on Render or Replit for public access

---

## ❓ Need Help?

If you have trouble running this, feel free to reach out or raise an issue.

Enjoy GradAtlas! 🎓

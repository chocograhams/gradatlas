from flask import Flask, jsonify, request, render_template, redirect, send_file, Response
import json
import os
import csv
import io
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Meetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100))
    details = db.Column(db.Text)
    location = db.Column(db.String(100))
    attendees = db.Column(db.Integer)
    tags = db.Column(db.Text)  # Comma-separated string

# --- Create Tables (for Render compatibility) ---
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def home():
    return "Meetup API is running. Try /meetups, /meetups/tag/<tag>, or /add"

@app.route('/meetups', methods=['GET'])
def get_all_meetups():
    meetups = Meetup.query.all()
    return jsonify([{
        "name": m.name,
        "host": m.host,
        "details": m.details,
        "location": m.location,
        "attendees": m.attendees,
        "tags": m.tags.split(",")
    } for m in meetups])

@app.route('/meetups/tag/<path:tag>', methods=['GET'])
def get_meetups_by_tag(tag):
    tag_lower = tag.strip().lower()
    meetups = Meetup.query.all()
    filtered = [m for m in meetups if tag_lower in [t.strip().lower() for t in m.tags.split(',')]]
    return jsonify([{
        "name": m.name,
        "host": m.host,
        "details": m.details,
        "location": m.location,
        "attendees": m.attendees,
        "tags": m.tags.split(",")
    } for m in filtered]) if filtered else jsonify({"error": f"No event found with tag '{tag}'"}), 404

@app.route('/meetups/location/<path:location>', methods=['GET'])
def get_meetups_by_location(location):
    location_lower = location.strip().lower()
    meetups = Meetup.query.filter(Meetup.location.ilike(f"%{location_lower}%")).all()
    if not meetups:
        return jsonify({"error": f"No event found in '{location}'"}), 404
    return jsonify([{
        "name": m.name,
        "host": m.host,
        "details": m.details,
        "location": m.location,
        "attendees": m.attendees,
        "tags": m.tags.split(",")
    } for m in meetups])

@app.route('/meetups/name/<path:name>', methods=['GET'])
def get_meetup_by_name(name):
    m = Meetup.query.filter(Meetup.name.ilike(name)).first()
    if m:
        return jsonify({
            "name": m.name,
            "host": m.host,
            "details": m.details,
            "location": m.location,
            "attendees": m.attendees,
            "tags": m.tags.split(",")
        })
    return jsonify({"error": f"No event found with name '{name}'"}), 404

@app.route('/api', methods=['GET'])
def api_index():
    return jsonify({
        "endpoints": [
            "/meetups",
            "/meetups/tag/<tag>",
            "/meetups/location/<location>",
            "/meetups/name/<name>",
            "/meetups/sort/attendees",
            "/meetups/delete/<name>",
            "/add (form)"
        ]
    })

@app.route('/meetups/search')
def search_meetups_api():
    field = request.args.get('field')
    query = request.args.get('q', '').strip().lower()
    meetups = Meetup.query.all()
    results = []

    for m in meetups:
        if field == "tag" and any(query in t.lower() for t in m.tags.split(',')):
            results.append(m)
        elif field == "location" and query in (m.location or "").lower():
            results.append(m)
        elif field == "name" and query in (m.name or "").lower():
            results.append(m)
        elif field == "details" and query in (m.details or "").lower():
            results.append(m)

    if results:
        return jsonify([{
            "name": m.name,
            "host": m.host,
            "details": m.details,
            "location": m.location,
            "attendees": m.attendees,
            "tags": m.tags.split(",")
        } for m in results])
    return jsonify({"error": "No event found matching your search."})

@app.route('/search')
def show_search_page():
    return render_template("search_meetups_with_export_logo_welcome.html")

@app.route('/add', methods=['GET', 'POST'])
def add_meetup():
    if request.method == 'POST':
        new_meetup = Meetup(
            name=request.form['name'],
            host=request.form['host'],
            details=request.form['details'],
            location=request.form['location'],
            attendees=int(request.form['attendees']),
            tags=','.join(tag.strip() for tag in request.form['tags'].split(','))
        )
        db.session.add(new_meetup)
        db.session.commit()
        print("Meetup saved to database.")
        return redirect('/meetups')
    return render_template("add_meetup.html")

@app.route('/meetups/export')
def export_meetups_to_csv():
    field = request.args.get('field')
    query = request.args.get('q', '').strip().lower()
    meetups = Meetup.query.all()

    def matches(m):
        if field == "tag":
            return any(query in t.lower() for t in m.tags.split(','))
        elif field == "location":
            return query in (m.location or "").lower()
        elif field == "name":
            return query in (m.name or "").lower()
        elif field == "details":
            return query in (m.details or "").lower()
        return False

    filtered = [m for m in meetups if matches(m)]

    def generate_csv():
        header = ['name', 'host', 'details', 'location', 'attendees', 'tags']
        yield ','.join(header) + '\n'
        for m in filtered:
            row = [
                m.name,
                m.host,
                m.details.replace(',', ';') if m.details else "",
                m.location,
                str(m.attendees),
                '; '.join(m.tags.split(',')) if m.tags else ''
            ]
            yield ','.join(f'"{c}"' for c in row) + '\n'

    return Response(generate_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=meetups_export.csv"})

@app.route('/meetups/export-selected', methods=['POST'])
def export_selected_to_csv():
    selected = request.json.get("selected", [])

    if not selected:
        return jsonify({"error": "No data provided"}), 400

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['name', 'host', 'details', 'location', 'attendees', 'tags'])
    writer.writeheader()
    for item in selected:
        writer.writerow({
            "name": item.get("name", ""),
            "host": item.get("host", ""),
            "details": item.get("details", ""),
            "location": item.get("location", ""),
            "attendees": item.get("attendees", 0),
            "tags": "; ".join(item.get("tags", []))
        })

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='selected_meetups.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

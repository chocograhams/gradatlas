from flask import Flask, jsonify, request, render_template, redirect
import json
import os
import csv
import io
from flask import send_file, Response

app = Flask(__name__)
DATA_FILE = "meetups-list.json"

def load_meetups():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_meetups(meetups):
    with open(DATA_FILE, "w") as f:
        json.dump(meetups, f, indent=2)

@app.route('/')
def home():
    return "Meetup API is running. Try /meetups, /meetups/tag/<tag>, or /add"

@app.route('/meetups', methods=['GET'])
def get_all_meetups():
    return jsonify(load_meetups())

@app.route('/meetups/tag/<path:tag>', methods=['GET'])
def get_meetups_by_tag(tag):
    tag_lower = tag.strip().lower()
    meetups = load_meetups()
    filtered = [
        m for m in meetups
        if any(t.lower() == tag_lower for t in m.get("tags", []))
    ]
    return jsonify(filtered) if filtered else jsonify({"error": f"No event found with tag '{tag}'"}), 404

@app.route('/meetups/location/<path:location>', methods=['GET'])
def get_meetups_by_location(location):
    location_lower = location.strip().lower()
    meetups = load_meetups()
    filtered = [
        m for m in meetups
        if location_lower in m.get("location", "").lower()
    ]
    return jsonify(filtered) if filtered else jsonify({"error": f"No event found in '{location}'"}), 404

@app.route('/meetups/name/<path:name>', methods=['GET'])
def get_meetup_by_name(name):
    name_lower = name.strip().lower()
    meetups = load_meetups()
    for m in meetups:
        if m['name'].strip().lower() == name_lower:
            return jsonify(m)
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
    meetups = load_meetups()
    results = []

    for m in meetups:
        if field == "tag":
            if any(query in t.lower() for t in m.get("tags", [])):
                results.append(m)
        elif field == "location":
            if query in m.get("location", "").lower():
                results.append(m)
        elif field == "name":
            if query in m.get("name", "").lower():
                results.append(m)
        elif field == "details":
            if query in m.get("details", "").lower():
                results.append(m)

    if results:
        return jsonify(results)
    return jsonify({"error": "No event found matching your search."})


@app.route('/search')
def show_search_page():
    return render_template("search_meetups_with_export_logo_welcome.html")

@app.route('/add', methods=['GET', 'POST'])
def add_meetup():
    if request.method == 'POST':
        new_meetup = {
            "name": request.form['name'],
            "host": request.form['host'],
            "details": request.form['details'],
            "location": request.form['location'],
            "attendees": int(request.form['attendees']),
            "tags": [tag.strip() for tag in request.form['tags'].split(',')]
        }
        meetups = load_meetups()
        meetups.append(new_meetup)
        save_meetups(meetups)
        print("Meetup saved to file.")
        return redirect('/meetups')
    return render_template("add_meetup.html")

@app.route('/meetups/export')
def export_meetups_to_csv():
    field = request.args.get('field')
    query = request.args.get('q', '').strip().lower()
    meetups = load_meetups()

    def matches(m):
        if field == "tag":
            return any(query in t.lower() for t in m.get("tags", []))
        elif field == "location":
            return query in m.get("location", "").lower()
        elif field == "name":
            return query in m.get("name", "").lower()
        elif field == "details":
            return query in m.get("details", "").lower()
        return False

    filtered = [m for m in meetups if matches(m)]


    def generate_csv():
        header = ['name', 'host', 'details', 'location', 'attendees', 'tags']
        yield ','.join(header) + '\n'
        for m in filtered:
            row = [
                m.get("name", ""),
                m.get("host", ""),
                m.get("details", "").replace(',', ';'),
                m.get("location", ""),
                str(m.get("attendees", 0)),
                '; '.join(m.get("tags", []))
            ]
            yield ','.join(f'"{c}"' for c in row) + '\n'

    return Response(generate_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=meetups_export.csv"})


@app.route('/meetups/export-selected', methods=['POST'])
def export_selected_to_csv():
    selected = request.json.get("selected", [])

    if not selected:
        return jsonify({"error": "No data provided"}), 400

    # Create in-memory CSV file
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

    # Optional: Save to local folder
    os.makedirs("exports", exist_ok=True)
    with open("exports/selected_meetups.csv", "w") as f:
        f.write(output.getvalue())

    # Return file as download
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='selected_meetups.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
from flask import Flask, jsonify, request, render_template, redirect, send_file, Response
import os
import csv
import io
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
admin = Admin(app, name='GradAtlas Admin', template_mode='bootstrap4')

# Simple admin user for demonstration
class AdminUser(UserMixin):
    id = "admin"
    password = "gradpass"  # Change in production

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser()
    return None

# Models
class Meetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100))
    details = db.Column(db.Text)
    location = db.Column(db.String(100))
    attendees = db.Column(db.Integer)
    tags = db.Column(db.Text)

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/login")

admin.add_view(SecureModelView(Meetup, db.session))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return "Meetup API is running. Try /meetups, /meetups/tag/<tag>, or /admin"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'gradpass':
            user = AdminUser()
            login_user(user)
            return redirect('/admin')
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

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
    meetups = Meetup.query.filter(Meetup.location.ilike(f"%{location.strip().lower()}%")).all()
    return jsonify([{
        "name": m.name,
        "host": m.host,
        "details": m.details,
        "location": m.location,
        "attendees": m.attendees,
        "tags": m.tags.split(",")
    } for m in meetups]) if meetups else jsonify({"error": f"No event found in '{location}'"}), 404

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
            "/meetups/search",
            "/meetups/export",
            "/admin"
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

    return jsonify([{
        "name": m.name,
        "host": m.host,
        "details": m.details,
        "location": m.location,
        "attendees": m.attendees,
        "tags": m.tags.split(",")
    } for m in results]) if results else jsonify({"error": "No event found matching your search."})

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
            return query in (m.location or '').lower()
        elif field == "name":
            return query in (m.name or '').lower()
        elif field == "details":
            return query in (m.details or '').lower()
        return False

    filtered = [m for m in meetups if matches(m)]

    def generate_csv():
        header = ['name', 'host', 'details', 'location', 'attendees', 'tags']
        yield ','.join(header) + '\n'
        for m in filtered:
            row = [
                m.name,
                m.host,
                m.details.replace(',', ';') if m.details else '',
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
        tags = item.get("tags", [])
        if isinstance(tags, str):
            tags = tags.split(',')
        writer.writerow({
            "name": item.get("name", ""),
            "host": item.get("host", ""),
            "details": item.get("details", ""),
            "location": item.get("location", ""),
            "attendees": item.get("attendees", 0),
            "tags": "; ".join(tags)
        })

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='selected_meetups.csv'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

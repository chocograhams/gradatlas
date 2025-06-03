from flask import Flask, jsonify, request, render_template, redirect, send_file, Response
import os
import csv
import io
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Login Manager ---
login_manager = LoginManager()
login_manager.init_app(app)

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Dummy credentials
dummy_users = {"admin": {"password": "password12345"}}

@login_manager.user_loader
def load_user(user_id):
    if user_id in dummy_users:
        return AdminUser(user_id)
    return None

# --- Models ---
class Meetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(100))
    details = db.Column(db.Text)
    location = db.Column(db.String(100))
    attendees = db.Column(db.Integer)
    tags = db.Column(db.Text)  # Comma-separated string

# --- Create Tables ---
with app.app_context():
    db.create_all()

# --- Flask-Admin Views ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')

admin = Admin(app, name='GradAtlas Admin', template_mode='bootstrap3', index_view=SecureAdminIndexView())
admin.add_view(SecureModelView(Meetup, db.session, name='Events'))

# --- Routes ---
@app.route('/')
def home():
    return "Meetup API is running. Try /meetups, /meetups/tag/<tag>, or /add"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in dummy_users and dummy_users[username]['password'] == password:
            user = AdminUser(username)
            login_user(user)
            return redirect('/admin')
        return "Invalid credentials", 401
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username"/><br>
            <input type="password" name="password" placeholder="Password"/><br>
            <input type="submit" value="Login"/>
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/meetups', methods=['GET'])
def get_all_meetups():
    meetups = Meetup.query.all()
    return jsonify([{ "name": m.name, "host": m.host, "details": m.details,
                      "location": m.location, "attendees": m.attendees,
                      "tags": m.tags.split(",") } for m in meetups])

@app.route('/meetups/tag/<path:tag>', methods=['GET'])
def get_meetups_by_tag(tag):
    tag_lower = tag.strip().lower()
    meetups = Meetup.query.all()
    filtered = [m for m in meetups if tag_lower in [t.strip().lower() for t in m.tags.split(',')]]
    return jsonify([{ "name": m.name, "host": m.host, "details": m.details,
                      "location": m.location, "attendees": m.attendees,
                      "tags": m.tags.split(",") } for m in filtered]) if filtered else jsonify({"error": f"No event found with tag '{tag}'"}), 404

@app.route('/meetups/location/<path:location>', methods=['GET'])
def get_meetups_by_location(location):
    location_lower = location.strip().lower()
    meetups = Meetup.query.filter(Meetup.location.ilike(f"%{location_lower}%")).all()
    if not meetups:
        return jsonify({"error": f"No event found in '{location}'"}), 404
    return jsonify([{ "name": m.name, "host": m.host, "details": m.details,
                      "location": m.location, "attendees": m.attendees,
                      "tags": m.tags.split(",") } for m in meetups])

@app.route('/meetups/name/<path:name>', methods=['GET'])
def get_meetup_by_name(name):
    m = Meetup.query.filter(Meetup.name.ilike(name)).first()
    if m:
        return jsonify({ "name": m.name, "host": m.host, "details": m.details,
                         "location": m.location, "attendees": m.attendees,
                         "tags": m.tags.split(",") })
    return jsonify({"error": f"No event found with name '{name}'"}), 404

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
        return jsonify([{ "name": m.name, "host": m.host, "details": m.details,
                          "location": m.location, "attendees": m.attendees,
                          "tags": m.tags.split(",") } for m in results])
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
        return redirect('/meetups')
    return render_template("add_meetup.html")

@app.route('/meetups/export-selected', methods=['POST'])
def export_selected():
    selected = request.json.get("selected", [])
    export_format = request.args.get("format", "csv")

    if not selected:
        return jsonify({"error": "No data provided"}), 400

    if export_format == "json":
        return jsonify(selected)

    elif export_format == "csv":
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
                "tags": "; ".join(item.get("tags", [])) if isinstance(item.get("tags"), list) else item.get("tags", "")
            })

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='selected_meetups.csv'
        )
    else:
        return jsonify({"error": "Invalid format. Use 'csv' or 'json'."}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

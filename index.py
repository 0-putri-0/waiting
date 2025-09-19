"""
app.py - Flask app that serves the UI and API endpoints
Run: python app.py
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import models

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
CORS(app)

# Ensure DB & tables exist
if not os.path.exists(models.DB):
    # If waiting.db missing, create and init tables
    try:
        import init_db
        init_db.init_db()
    except Exception:
        models.init_db_if_missing()
else:
    models.init_db_if_missing()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/staff")
def staff():
    return render_template("staff.html")

# API endpoints
@app.route("/api/tickets", methods=["GET"])
def api_list_tickets():
    status = request.args.get('status')
    tickets = models.list_tickets(status=status)
    return jsonify(tickets)

@app.route("/api/tickets", methods=["POST"])
def api_create_ticket():
    data = request.get_json() or {}
    name = data.get("name")
    ticket = models.create_ticket(name=name)
    return jsonify(ticket), 201

@app.route("/api/tickets/serve", methods=["POST"])
def api_serve_next():
    served = models.serve_next()
    if not served:
        return jsonify({"message": "No waiting ticket"}), 404
    return jsonify(served)

@app.route("/api/tickets/<int:tid>", methods=["PUT"])
def api_update_ticket(tid):
    data = request.get_json() or {}
    status = data.get("status")
    if status not in ("waiting", "served", "cancelled"):
        return jsonify({"error":"invalid status"}), 400
    try:
        models.update_status(tid, status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True})

# Static file fallback (optional)
@app.route("/<path:path>")
def static_proxy(path):
    # allow direct access to static assets if needed
    return send_from_directory('static', path)

if __name__ == "__main__":
    # For testing only — use a real WSGI server for production
    app.run(host="127.0.0.1", port=8080, debug=True)

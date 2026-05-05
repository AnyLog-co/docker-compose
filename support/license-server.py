from flask import Flask, request, jsonify
from datetime import datetime
import csv, os

app = Flask(__name__)
LOG_FILE = "license_acceptances.csv"

FIELDS = ["name", "company", "email", "project", "license_key", "timestamp"]

@app.route("/api/license-accept", methods=["POST"])
def license_accept():
    # force=True accepts body even if Content-Type header is slightly off
    # silent=False surfaces parse errors rather than returning None quietly
    data = request.get_json(force=True, silent=False)

    if data is None:
        return jsonify({"error": "Request body is not valid JSON"}), 400

    missing = [k for k in FIELDS if k not in data]
    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 400

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ["received_at"],
                                extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow({**data, "received_at": datetime.utcnow().isoformat()})

    print(f"[{datetime.utcnow()}] Accepted: {data['name']} <{data['email']}> "
          f"({data['company']}) — {data['project']} — key: {data['license_key'][:16]}...")
    return jsonify({"status": "accepted"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)

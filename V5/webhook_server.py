from flask import Flask, request, jsonify
from sheets_utils import update_appointment_by_name

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Webhook received:", data)

    # Vapi will send: {"name": "Ram", "status": "Coming"}
    name = data.get("name")
    status = data.get("status")

    if name and status:
        updated = update_appointment_by_name(name, status)
        if updated:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "not_found"}), 404

    return jsonify({"error": "Invalid payload"}), 400


if __name__ == "__main__":
    app.run(port=5001, debug=True)

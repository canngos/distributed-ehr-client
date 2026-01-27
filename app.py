from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
import uuid

app = Flask(__name__)

# Backend EHR service base URL
# For local testing
EHR_BASE_URL = os.getenv("EHR_BASE_URL", "http://localhost:8001")


@app.route("/")
def home():
    return "ehr-client is running"

# Health Check Endpoint


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ehr-client"}), 200


@app.route("/")
def home():
    return "ehr-client is running"

# POST (UI and API part)


@app.route("/client/patient/create", methods=["POST"])
def create_patient():

    payload = request.get_json(silent=True)

    if payload:
        # Input validation, add required fields to list below
        required_fields = ["patient_id", "name", "birth_date"]
        for i in required_fields:
            if i not in payload:
                return {"message": "Missing required data"}, 400

        # Create record of the entered data
        patient_information = {
            "id": str(uuid.uuid4()),
            "patient_id": payload.get("patient_id"),
            "name": payload.get("name"),
            "birth_date": payload.get("birth_date"),
            "height": payload.get("height"),
            "weight": payload.get("weight"),
            "blood_type": payload.get("blood_type"),
            "created_at": datetime.now().isoformat()
        }

        # Post patient information to backend
        try:
            backend_res = requests.post(
                f"{EHR_BASE_URL}/patient/create",
                json=patient_information,
                timeout=5
            )
        except requests.RequestException as e:
            return jsonify({"error": "Backend not reachable", "details": str(e)}), 503

        try:
            return jsonify(backend_res.json()), backend_res.status_code
        except ValueError:
            return backend_res.text, backend_res.status_code

    # return error message and 400 if no payload is provided
    return {"message": "No JSON data received"}, 400


# GET (UI and API part)


# Is this UUID method viable?
@app.route("/client/patient/<patient_id>", methods=["GET"])
def read_patient_data(patient_id):

    # Check if the patient ID excists in DB
    if not patient_id:
        return {"message": "No such patient ID in database"}, 400

    # Get patient data from backend
    try:
        backend_res = request.get(
            f"{EHR_BASE_URL}/patient/{patient_id}",
            timeout=5
        )
    except request.RequestException as e:
        return jsonify({"error": "Backend not reachable", "details": str(e)}), 503

    # Deliver the data to client

    try:
        return jsonify(backend_res.json()), backend_res.status_code
    except ValueError:
        return backend_res.text, backend_res.status_code


# add route endpoint to get all the data?
# @app.route("/client/patient", methods=["GET"])
# def get_all_data:

# Update (UI and API Part)


@app.route("/client/patient/update", methods=["PUT"])
def update_patient():
    # Read incoming JSON body from user/client
    payload = request.get_json(silent=True) or {}

    patient_id = payload.get("patient_id")
    data = payload.get("data", {})

    # Validate inputs
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400
    if not isinstance(data, dict) or len(data) == 0:
        return jsonify({"error": "data must be a non-empty JSON object"}), 400

    # Build backend URL
    backend_url = f"{EHR_BASE_URL}/patients/{patient_id}"

    # Forward request to backend (API Part)
    try:
        backend_res = requests.put(backend_url, json=data, timeout=5)
    except requests.RequestException as e:
        return jsonify({"error": "Backend not reachable", "details": str(e)}), 503

    # Return backend response to the caller
    try:
        return jsonify(backend_res.json()), backend_res.status_code
    except ValueError:
        return backend_res.text, backend_res.status_code

# Delete (UI and API Part)


@app.route("/client/patient/delete/<patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    backend_url = f"{EHR_BASE_URL}/patients/{patient_id}"

    try:
        backend_res = requests.delete(backend_url, timeout=5)
    except requests.RequestException as e:
        return jsonify({"error": "Backend not reachable", "details": str(e)}), 503

    try:
        return jsonify(backend_res.json()), backend_res.status_code
    except ValueError:
        return backend_res.text, backend_res.status_code


if (__name__ == "__main__"):
    app.run(host="0.0.0.0", port=5000, debug=True)

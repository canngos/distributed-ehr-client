from flask import Flask, request, jsonify
import os
import requests
import uuid
from datetime import datetime

app = Flask(__name__)

EHR_BASE_URL = os.getenv("EHR_BASE_URL", "http://localhost:8001")


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


@app.route("/client/patient", methods=["GET"])
def get_all_data:


if (__name__ == "__main__"):
    app.run(host="0.0.0.0", port=5000, debug=True)

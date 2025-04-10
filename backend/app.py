from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store latest sensor data in memory
latest_data = {"temperature": None, "humidity": None, "latitude": None, "longitude": None, "package_id": None, "timestamp": None}

@app.route("/")
def index():
    return render_template("index.html")


from playsound import playsound
import threading

def play_beep():
    playsound("beep.wav")

@app.route("/update", methods=["POST"])
def update():
    data = request.json

    if not data:
        return "Bad Request: No JSON received", 400
  
    # Update stored data
    if "temperature" in data:
        latest_data["temperature"] = data["temperature"]
    if "humidity" in data:
        latest_data["humidity"] = data["humidity"]
    if "latitude" in data:
        latest_data["latitude"] = data["latitude"]
    if "longitude" in data:
        latest_data["longitude"] = data["longitude"]
    if "package_id" in data:
        latest_data["package_id"] = data["package_id"]
    latest_data["timestamp"] = datetime.utcnow().strftime("%d %B, %Y - %H:%M:%S")

    return jsonify(latest_data), 200


@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(latest_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# Database connection parameters
DB_CONFIG = {
    "dbname": "iot_db_db_new_changed_new",
    "user": "postgres",
    "port": "5433"
}

# Store latest sensor data in memory
latest_data = {"temperature": None, "humidity": None, "latitude": None, "longitude": None, "package_id": None, "timestamp": None}

def get_db_connection():
    """Hiii there 1"""
    try:
        """Create and return the connection"""
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def save_package_data(data):
    """Save package data to database, and return a bool"""
    if not data.get("package_id"):
        return False
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO package_data 
                (package_id, temperature, humidity, latitude, longitude, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    data["package_id"],
                    data.get("temperature"),
                    data.get("humidity"),
                    data.get("latitude"),
                    data.get("longitude"),
                    datetime.utcnow()
                )
            )
            conn.commit()
            
            # Check for temperature alert
            if data.get("temperature") is not None and float(data["temperature"]) > 40:
                create_alert(data["package_id"], "Temperature", float(data["temperature"]), 40, 
                             f"High temperature alert: {data['temperature']}°C exceeded threshold of 40°C")
            
            # Check for humidity alert
            if data.get("humidity") is not None and float(data["humidity"]) > 65:
                create_alert(data["package_id"], "Humidity", float(data["humidity"]), 65,
                             f"High humidity alert: {data['humidity']}% exceeded threshold of 65%")
            
            return True
    except Exception as e:
        print(f"Error saving package data: {e}")
        return False
    finally:
        conn.close()

def create_alert(package_id, alert_type, value, threshold, message):
    """Create an alert in the database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO alerts 
                (package_id, type, value, threshold, message, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (package_id, alert_type, value, threshold, message, datetime.utcnow())
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error creating alert: {e}")
        return False
    finally:
        conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update", methods=["POST"])
def update():
    data = request.json

    if not data:
        return "Bad Request: No JSON received", 400
  
    # Make a copy of data to avoid modifying during iteration
    update_data = {}
    
    # Update stored data
    if "temperature" in data:
        latest_data["temperature"] = data["temperature"]
        update_data["temperature"] = data["temperature"]
    if "humidity" in data:
        latest_data["humidity"] = data["humidity"]
        update_data["humidity"] = data["humidity"]
    if "latitude" in data:
        latest_data["latitude"] = data["latitude"]
        update_data["latitude"] = data["latitude"]
    if "longitude" in data:
        latest_data["longitude"] = data["longitude"]
        update_data["longitude"] = data["longitude"]
    if "package_id" in data:
        latest_data["package_id"] = data["package_id"]
        update_data["package_id"] = data["package_id"]
    
    current_time = datetime.utcnow()
    latest_data["timestamp"] = current_time.strftime("%d %B, %Y - %H:%M:%S")
    
    # Only try to save to database if we have a package_id
    if latest_data["package_id"]:
        # Use the combined data from latest_data to ensure we have all fields
        db_data = {
            "package_id": latest_data["package_id"],
            "temperature": latest_data["temperature"],
            "humidity": latest_data["humidity"],
            "latitude": latest_data["latitude"],
            "longitude": latest_data["longitude"]
        }
        save_package_data(db_data)

    return jsonify(latest_data), 200

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(latest_data)

@app.route("/alerts", methods=["GET"])
def get_alerts():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT 20
                """
            )
            alerts = cur.fetchall()
            return jsonify(list(alerts)), 200
    except Exception as e:
        print(f"Error retrieving alerts: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

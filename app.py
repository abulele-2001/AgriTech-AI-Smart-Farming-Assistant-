import os, base64, sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agritech.db"
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, field TEXT NOT NULL, planted TEXT,
            stage TEXT, health TEXT DEFAULT 'Healthy', notes TEXT DEFAULT ''
        )""")
        count = conn.execute("SELECT COUNT(*) FROM crops").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO crops(name,field,planted,stage,health,notes) VALUES(?,?,?,?,?,?)",
                [
                    ("Maize", "North Field", "2026-09-12", "Vegetative", "Healthy", "Monitor soil moisture weekly"),
                    ("Tomatoes", "Greenhouse 1", "2026-09-03", "Flowering", "Attention", "Check lower leaves for spotting"),
                    ("Butternut", "South Field", "2026-08-20", "Fruiting", "Healthy", "Maintain consistent irrigation"),
                ],
            )

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/crops")
def get_crops():
    with db() as conn:
        rows = conn.execute("SELECT * FROM crops ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/crops")
def add_crop():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    field = (data.get("field") or "").strip()
    if not name or not field:
        return jsonify({"error": "Crop name and field are required."}), 400
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO crops(name,field,planted,stage,health,notes) VALUES(?,?,?,?,?,?)",
            (name, field, data.get("planted", ""), data.get("stage", "Seedling"), "Healthy", data.get("notes", "")),
        )
        crop = conn.execute("SELECT * FROM crops WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(crop)), 201

def openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI
    return OpenAI(api_key=key)

@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please enter a question."}), 400
    try:
        client = openai_client()
        if client:
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                instructions=("You are AgriTech AI, a practical farming information assistant. "
                              "Give clear, cautious, locally adaptable advice. Ask for crop, location, "
                              "growth stage and symptoms when important. Do not present guesses as diagnoses. "
                              "For serious crop loss, recommend contacting a local agricultural extension officer."),
                input=message
            )
            return jsonify({"reply": response.output_text, "mode": "ai"})
    except Exception as exc:
        app.logger.exception("AI chat failed")
        return jsonify({"error": "AI service could not respond. Check your API key and connection."}), 502

    return jsonify({
        "mode": "demo",
        "reply": "Demo mode is active. Add your OPENAI_API_KEY to the .env file to enable live AI answers. "
                 "For better guidance, include your crop, growth stage, location and what you have observed. "
                 "I can help you think through irrigation, soil health, pests and crop-care questions."
    })

@app.post("/api/diagnose")
def diagnose():
    image = request.files.get("image")
    crop = request.form.get("crop", "Unknown crop")
    notes = request.form.get("notes", "")
    if not image:
        return jsonify({"error": "Please upload a plant image."}), 400
    if image.mimetype not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        return jsonify({"error": "Upload a JPG, PNG, WEBP or GIF image."}), 400
    raw = image.read()
    try:
        client = openai_client()
        if client:
            encoded = base64.b64encode(raw).decode("utf-8")
            data_url = f"data:{image.mimetype};base64,{encoded}"
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                instructions=("You are a cautious crop-health assistant. Examine the supplied plant photo "
                              "and user notes. Explain visible signs, possible causes, confidence and safe next "
                              "steps. Do not claim certainty from one photo. Ask for a clearer close-up or "
                              "local expert confirmation when needed. Do not prescribe regulated chemicals."),
                input=[{"role": "user", "content": [
                    {"type": "input_text", "text": f"Crop: {crop}. Notes: {notes or 'None supplied'}. "
                     "Assess visible plant health and suggest next steps."},
                    {"type": "input_image", "image_url": data_url, "detail": "auto"}
                ]}]
            )
            return jsonify({"analysis": response.output_text, "mode": "ai"})
    except Exception:
        app.logger.exception("Image diagnosis failed")
        return jsonify({"error": "Image analysis failed. Check your API key, model access and connection."}), 502

    return jsonify({
        "mode": "demo",
        "analysis": "Demo analysis: your image has been received, but live image recognition is not enabled yet. "
                    "Add an OpenAI API key in your .env file to activate photo analysis. "
                    "For a useful assessment, upload a sharp image of the affected leaf (front and underside), "
                    "include the crop variety, growth stage, recent weather and when symptoms began. "
                    "Do not apply treatment based on this demo result."
    })

@app.get("/api/health")
def health():
    return jsonify({"status": "online", "ai_enabled": bool(os.getenv("OPENAI_API_KEY"))})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)

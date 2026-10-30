# AgriTech AI — Smart Farming Assistant

A responsive agricultural technology dashboard built with HTML, CSS, JavaScript, Python (Flask) and SQLite. It includes crop records, a farming chat assistant, an image-based crop health assessment workflow, soil and irrigation notes, equipment examples and CSV reporting.

## Features

- Responsive dashboard and navigation
- Crop management with records saved in SQLite
- AI farming assistant endpoint
- Plant photo upload and vision-analysis endpoint
- Soil and irrigation information panel
- Equipment hub (illustrative sample listings)
- CSV export for crop records
- Demo mode when no API key is configured

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Extract the ZIP and open the `agritech_ai` folder in VS Code.
3. Open a terminal in that folder.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Optional: activate live AI features:
   - Copy `.env.example` to a new file named `.env`.
   - Add your own API key after `OPENAI_API_KEY=`.
   - Keep `.env` private and never commit it to GitHub.
   - You may change `OPENAI_MODEL` to a vision-capable model available to your API account.

7. Start the application:

   ```powershell
   python app.py
   ```

8. Open `http://127.0.0.1:5000` in your browser.

The SQLite database `agritech.db` is created automatically on first run with sample crop records.

## Important notes

- Without an API key, the app runs in demo mode. The image upload and chat workflows are connected to the backend, but AI-generated results require a configured API key and internet access.
- Weather readings, farm metrics, soil values and equipment listings currently contain sample/demo data. They are not live sensor readings, forecasts, supplier inventory or agronomic recommendations.
- AI crop assessments are informational and can be wrong. They are not a substitute for laboratory testing or advice from an agricultural extension officer / qualified agronomist.
- This starter project does not include user authentication, production hosting, live weather integration, IoT sensor ingestion or a verified plant-disease classifier model. These are suitable next development milestones.

## Project structure

```text
agritech_ai/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

## Suggested next milestones

1. Add user registration, login and farm-level permissions.
2. Integrate a trusted weather API for a farm's selected coordinates.
3. Add field boundaries, GPS mapping and sensor readings.
4. Add an audited crop-disease dataset and evaluate a dedicated classifier.
5. Add SQL Server support and database migrations.
6. Deploy with HTTPS, secure secrets, logging, backups and rate limits.

## GitHub safety

Create a `.gitignore` containing:

```gitignore
.env
.venv/
__pycache__/
*.pyc
agritech.db
```

Never publish API keys, passwords or private farm data.

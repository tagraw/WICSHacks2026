# ACL 2026 Concert Safety App Scaffold

A hackathon-ready scaffold for the ACL 2026 Safety & Accessibility App.

## Features

-   **Frontend**: React (Vite) + Tailwind CSS + Lucide Icons
-   **Backend**: FastAPI + Python
-   **ML**: Scikit-learn (Crowd Risk Prediction Placeholder)
-   **Data**: SerpAPI Integration (Live Weather/News Alerts)
-   **Infrastructure**: Docker Compose (One-command setup)

## Tech Stack

-   **Frontend**: React, Vite, TailwindCSS, Axios
-   **Backend**: FastAPI, Uvicorn, Pandas, Scikit-learn
-   **Map**: Google Maps / Mapbox Ready (Requires API Key)

## Getting Started

### Prerequisites

-   Docker & Docker Compose installed
-   (Optional) API Keys for SerpAPI and Google Maps

### ONE-COMMAND START

1.  **Clone the repo**
2.  **Set up environment variables**:
    ```bash
    cp .env.example .env
    # Edit .env and add your SERPAPI_KEY if you have one
    ```
3.  **Run with Docker Compose**:
    ```bash
    docker compose up --build
    ```

### 1. Backend (Docker)
```bash
docker compose up --build
```
*Runs on http://localhost:8000*

### 2. Frontend (React Native Mobile App)

Open a new terminal:
```bash
cd frontend
npx expo start
```
-   **Scan QR Code**: Use the **Expo Go** app on your Android/iOS device.
-   **Emulators**: Press `a` for Android Emulator or `i` for iOS Simulator.

### Accessing the App

-   **Mobile App**: via Expo Go or Emulator
-   **Backend Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints (Sample)

-   `POST /ping-location`: Send device location to update crowd density.
-   `GET /heatmap`: Get crowd density data.
-   `POST /safe-route`: detailed safe route coordinates.
-   `GET /live-alerts`: Get real-time alerts from SerpAPI.
-   `POST /sos`: Trigger emergency alert.

## ML Pipeline (Mock)

The `ml_service.py` currently contains a mock `RandomForestClassifier` trained on dummy data to predict crowd risk (Low/Medium/High) based on density, time, and terrain.

## Hackathon Tips

-   **Modify `ml_service.py`** to use real data or a more complex model.
-   **Update `App.jsx`** to replace the map placeholder with `react-google-maps` using your key.
-   **Customize `tailwind.config.js`** for different branding.

Happy Hacking! 🚀

Here is a polished and well-structured `README.md` for your repository. It builds upon the existing content and structures it to be professional and visually appealing.

-----

# 📖 VerseTrack (BibleTracker)

VerseTrack is a comprehensive, gamified Bible reading tracker designed to keep users engaged and consistent in their faith journey. Whether you're tracking daily progress or reading along with friends, VerseTrack offers a modern, interactive way to stay accountable and dive deeper into the Word.

## ✨ Features

  - **📅 Flexible Reading Plans:** Tailor your reading schedule to fit your lifestyle and spiritual goals.
  - **🔥 GitHub-Style Heat Maps:** Visually track your daily consistency with an intuitive progress heat map.
  - **🤖 AI-Powered Chapter Summaries:** Gain deeper insights into scripture with automated summaries powered by Emergent LLM.
  - **👥 Reading Circles:** Form communal groups to foster accountability, share progress, and encourage each other in your faith journey.

## 🛠 Tech Stack

  - **Frontend:** TypeScript, Expo / React Native
  - **Backend:** Python, FastAPI (Uvicorn)
  - **AI Integration:** Emergent LLM

## 📂 Project Structure

```bash
BibleTracker/
├── backend/          # Python backend (FastAPI)
├── frontend/         # TypeScript / Expo mobile app
├── memory/           # Memory storage/context
├── tests/            # Test suite 
├── test_reports/     # Generated reports for testing
└── .emergent/        # Emergent LLM configurations
```

## 🚀 Getting Started

Follow these steps to run VerseTrack locally on your machine.

### Prerequisites

  - Node.js & npm
  - Python 3.8+
  - Expo CLI

### 1\. Clone the Repository

```bash
git clone https://github.com/YshuaManzano/BibleTracker.git
cd BibleTracker
```

### 2\. Setup the Environment Variables

Create a `.env` file based on the provided `.env.example` in both the `backend` and `frontend` directories.

> **Note:** Ensure you include your **Emergent LLM key** in the backend environment variables to enable the AI chapter summaries.

### 3\. Install and Run the Backend

Navigate to the backend directory, install the required Python packages, and start the local server.

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

### 4\. Install and Run the Frontend

Open a new terminal, navigate to the frontend directory, install Node modules, and launch the Expo development server.

```bash
cd frontend
npm install
npx expo start
```

## 🤝 Contributors

  - **[YshuaManzano](https://www.google.com/search?q=https://github.com/YshuaManzano)** ---
    *If you find this project helpful, please consider giving it a ⭐ on GitHub\!*

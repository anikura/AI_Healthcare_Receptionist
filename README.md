# 🏥 AI Healthcare Receptionist

A sophisticated, full-stack virtual healthcare assistant designed to streamline hospital operations. This project leverages Large Language Models (LLMs) to handle patient interactions, appointment management, and preliminary symptom analysis via text and voice.

## 🎥 Project Demo

> **Watch the complete project demonstration here:**
> **🔗 https://drive.google.com/file/d/1dr7saqW-AP9ObJDcfcFMJ4Q6ptQa0MH2/view?usp=sharing**

---

## 🚀 Key Features

* **Intelligent Intent Recognition:** Uses LLM-based classification to detect user needs like booking, viewing, or cancelling appointments.
* **End-to-End Appointment Management:** Fully automated workflow from data collection to database storage in MongoDB.
* **Voice Integration:** Supports voice-to-text (Whisper) for patient input and text-to-speech (Edge-TTS) for assistant responses.
* **Symptom Analysis:** Preliminary health assessment that recommends specific hospital departments based on patient input.
* **Knowledge Base Integration:** Real-time access to hospital details, doctor specializations, and office locations.
* **Security:** Implements data encryption for sensitive patient information (Name, Phone, Email) using Fernet.

## 🛠️ Technical Stack

* **Frontend:** Streamlit
* **AI Engine:** Claude-3.5-Sonnet (via Anthropic API) & Ollama (for local intent detection)
* **Database:** MongoDB (with a local MockDB fallback for development)
* **Audio Processing:** OpenAI Whisper & Edge-TTS
* **Environment:** Python 3.x, Dotenv configuration

## 📋 Prerequisites

* Python 3.8+
* MongoDB Atlas account (or local MongoDB)
* Anthropic API Key

## 🔧 Installation & Setup

1. **Clone the Repository:**

   ```bash
   git clone <your-repo-url>
   cd <folder-name>
   ```

2. **Install Dependencies:**

   ```bash
   pip install streamlit pymongo anthropic ollama whisper edge-tts cryptography sounddevice scipy
   ```

3. **Configure Environment Variables:**

   Create a `.env` file in the root directory and add your credentials:

   ```env
   ANTHROPIC_API_KEY=your_key_here
   MONGO_URI=your_mongodb_uri
   DB_NAME=healthcare_assistant
   ```

4. **Run the Application:**

   ```bash
   streamlit run app_organized.py
   ```

## 📂 Project Structure

* `app_organized.py`: Main Streamlit UI and session management logic.
* `ai_engine.py`: Core logic for managing conversation state and symptom analysis.
* `backend.py`: Handles database connections, encryption, and audio processing.
* `validators.py`: Data cleaning and validation for patient records.
* `Knowledge_Base.json`: Static data for hospital departments and doctors.

## 📝 Disclaimer

This AI assistant provides preliminary guidance and administrative support. It is **not** a substitute for professional medical advice, diagnosis, or treatment.

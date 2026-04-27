# Estecharat AI Customer Support Agent

Estecharat AI is a standalone Python microservice that acts as an intelligent, bilingual (English/Arabic) virtual assistant for the Estecharat Medical Platform. 

It is built using **FastAPI** and **LangChain**, utilizing OpenAI's `gpt-4o-mini` model. The AI is designed to help patients identify appropriate medical specialties based on their symptoms, recommend available doctors, check doctor time slot availability, and answer general platform FAQs.

## Architecture & How it Works

Instead of having direct access to the PostgreSQL database (which is a security risk and computationally heavy), the AI acts as an independent agent. It communicates securely with the core **Java Spring Boot Backend** via isolated internal APIs using a shared secret key (`X-Internal-Secret`).

When a patient asks a question, the AI intelligently decides which "Tools" to use (e.g., `search_doctors`, `get_doctor_availability`), fetches the live data from the Java backend, and formulates a helpful, conversational response.

## Prerequisites

- **Python 3.11+**
- **Java Spring Boot Backend** running on `localhost:7002` (The AI relies on endpoints like `/api/internal/ai/doctors`)
- **OpenAI API Key**

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohamedOmar336/estecharat-ai.git
   cd estecharat-ai
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Rename the `.env.example` file to `.env` and insert your API keys:
   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   JAVA_BACKEND_URL=http://localhost:7002
   INTERNAL_API_SECRET=estecharat_ai_secret_key_2026
   ```

## Running the AI Server

Once your Java backend is up and running, you can start the AI microservice.

```bash
python main.py
```

The server will start on `http://localhost:8000`. It exposes the `/api/ai/chat` endpoint, which the Angular frontend portal communicates with to provide the chat UI.

## Testing the API

You can test the AI agent using Postman or cURL:

```bash
curl -X POST http://localhost:8000/api/ai/chat \
-H "Content-Type: application/json" \
-d '{"session_id": "patient_001", "message": "I have continuous chest pain, who should I talk to?"}'
```

*(Note: The `session_id` is used by the AI to remember the conversation history. If a user is logged in, their user ID should be used as the session ID).*

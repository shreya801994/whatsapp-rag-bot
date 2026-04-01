# Local WhatsApp RAG Bot 🤖📱

A fully local, privacy-first WhatsApp bot that allows you to chat with your PDF documents. 

This project uses **Retrieval-Augmented Generation (RAG)** to ingest PDFs, convert them into searchable vector embeddings, and answer user questions using a local Large Language Model (LLM)—all while communicating through the Twilio WhatsApp API. 

**Zero data leaves your machine.** No OpenAI APIs, no cloud LLM costs, and complete privacy for your documents.

## 🚀 Key Features

* **100% Local Processing:** Uses `Ollama` to run models like Mistral or Llama 3 directly on your hardware. 
* **Asynchronous Background Threading:** Twilio requires a webhook response within 15 seconds, but local LLMs on a CPU can take minutes to generate an answer. This bot uses Python's `threading` to instantly satisfy Twilio's HTTP request while the heavy AI processing happens in the background. Once finished, the bot initiates a new outbound message to the user.
* **Fully Dockerized:** The entire architecture (Flask Webhook, ChromaDB, Ollama) is containerized with `docker-compose` for easy deployment.
* **Vector Database:** Uses `ChromaDB` and `all-MiniLM-L6-v2` embeddings for fast and accurate document retrieval.

## 🏗️ Architecture

1. **Flask Webhook Container:** Receives incoming WhatsApp messages/PDFs via Twilio.
2. **Ingest Script:** Extracts text from uploaded PDFs, chunks it, embeds it, and saves it to the vector database.
3. **ChromaDB Container:** Stores the vector embeddings.
4. **Ollama Container:** Runs the local LLM to generate answers based on the retrieved context.

## 📋 Prerequisites

To run this project, you will need:
* **Docker & Docker Compose** installed (with WSL2 enabled if on Windows).
* A **Twilio Account** with the WhatsApp Sandbox activated.
* A local tunneling tool like **ngrok** or **cloudflared** to expose your local port 5000 to the internet.
* **Hardware:** A machine with at least 12GB+ of RAM allocated to Docker/WSL.

## 🛠️ Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/whatsapp-rag-bot.git](https://github.com/YourUsername/whatsapp-rag-bot.git)
cd whatsapp-rag-bot
```

**2. Set up Environment Variables**
Create a `.env` file in the root directory and add your Twilio credentials. **(Never commit this file to GitHub!)**
```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
```

**3. Build and Start the Containers**
```bash
docker compose up -d --build
```

**4. Download the Local LLM**
Once the containers are running, you need to pull your model of choice (e.g., Mistral) into the Ollama container:
```bash
docker compose exec ollama ollama pull mistral
```
*(Note: If you want to use a faster/smaller model for CPU processing, you can pull `llama3.2` and update the `MODEL_NAME` in `rag.py`)*

## 🔗 Connecting to WhatsApp

1. Start your local tunnel to expose port 5000:
   ```bash
   ngrok http 5000
   ```
2. Copy the forwarded `https` URL ngrok gives you.
3. Go to your Twilio Console -> WhatsApp Sandbox Settings.
4. Paste the URL into the **"When a message comes in"** field and append `/whatsapp` to the end (e.g., `https://your-ngrok-url.app/whatsapp`). Save the settings.

## 💬 Usage

1. **Join the Sandbox:** Send the Twilio join code (e.g., `join something-something`) to the Sandbox number on WhatsApp.
2. **Upload a PDF:** Send a PDF document directly in the WhatsApp chat. The bot will instantly reply that it is processing the document in the background. 
3. **Ask Questions:** Once the bot confirms the document is ready, text it a question. The bot will reply with "Thinking about it... 🧠" and then push the final LLM-generated answer to your phone a few minutes later!

## 🚧 Version 1 Limitations & Future Roadmap
* **Stateless Chat:** Currently (V1), the bot answers single queries based on the document but does not remember chat history. 
* **Typed PDFs Only:** The ingest script extracts digital text. Scanned or handwritten PDFs currently return empty contexts (OCR support planned for V2).
* **CPU Inference:** Generation times take 1-3 minutes on standard CPUs.

---
*Built with Python, Flask, Docker, and caffeine.*
```

***

### How to add this to GitHub:
1. Open your project folder in your code editor (like VS Code).
2. Create a new file named `README.md`.
3. Paste the markdown code above into it.
4. Save the file.
5. In your PowerShell, run:
   ```powershell
   git add README.md
   git commit -m "docs: add comprehensive README for V1"
   git push

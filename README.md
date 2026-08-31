# PulseAI 🚀

PulseAI is an AI-powered news aggregation platform that automatically collects, summarizes, ranks, and delivers personalized AI news from multiple sources such as YouTube, OpenAI, and Anthropic.

It helps developers, researchers, and AI enthusiasts stay updated without spending hours reading articles or watching long videos.

---

## ✨ Features

- 🔥 Scrape AI news from YouTube channels
- 🤖 Fetch latest updates from OpenAI and Anthropic
- 📝 Generate concise summaries using Groq LLMs
- 🎯 Rank articles based on user interests
- 📧 Generate personalized email digests
- 🗄️ Store articles and digests in PostgreSQL
- ⚡ Automated daily pipeline

---

## 🏗️ Project Structure

```text
AI-NEWS/

├── app/
│   ├── agent/
│   │   ├── curator_agent.py
│   │   ├── digest_agent.py
│   │   └── email_agent.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── profiles/
│   │   └── user_profile.py
│   │
│   ├── scrapers/
│   │   ├── youtube.py
│   │   ├── openai.py
│   │   └── anthropic.py
│   │
│   ├── services/
│   │   ├── process_email.py
│   │   ├── process_digests.py
│   │   ├── process_transcripts.py
│   │   └── process_articles.py
│   │
│   ├── config.py
│   ├── daily_runner.py
│   └── runner.py
│
├── venv/
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

### Backend

- Python
- PostgreSQL
- SQLAlchemy
- Pydantic

### AI

- Groq API
- OpenAI API

### Data Sources

- YouTube RSS Feeds
- YouTube Transcript API
- OpenAI Blog
- Anthropic Blog

### Deployment


---

## 🚀 How It Works

```text
YouTube / OpenAI / Anthropic
              ↓
        Scrape content
              ↓
     Extract transcripts/articles
              ↓
       Generate AI summaries
              ↓
      Rank based on interests
              ↓
      Generate email digest
              ↓
         Send to users
```

---

## 🔧 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/pulse-ai.git

cd pulse-ai
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=

POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=

MY_EMAIL=
MY_PASSWORD=
TO_EMAIL=
```

---

## ▶️ Run Project

Start PostgreSQL:

```bash
docker-compose up -d
```

Run:

```bash
python main.py
```

---

## 📧 Example Output

- Personalized AI news digest
- Ranked articles
- Daily email summaries

Example:

- GPT-5.6 recursive self-improvement
- Gemini 3.6 updates
- OpenAI research announcements

---

## 🌟 Future Improvements

- User authentication
- React frontend
- Real-time notifications
- Search functionality
- Mobile application
- Recommendation engine

---

## 👨‍💻 Author

Vinay Boggula

GitHub: https://github.com/your-username

# FakeDetector 🔍

**The world's most comprehensive open-source fake detection platform.**

Powered by death. Free forever. No accounts required.

---

## Features

- 🤖 **AI Content Detection** — Detect AI-generated text
- 📋 **Plagiarism & Originality** — Check if ideas are copied
- 📰 **Fake News Detection** — Verify news credibility
- ⭐ **Fake Review Detection** — Spot bot/fake reviews
- 👤 **Fake Profile Detection** — Detect fake social profiles
- 💼 **Fake Job Detection** — Identify scam job postings
- 🎣 **Phishing Detection** — Detect phishing emails
- ⟨⟩ **Code Plagiarism** — Check code originality

**Input Methods:** Text, URL (live fetch), File Upload (TXT, PDF, DOCX)

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

Edit the `.env` file and add your Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

Get a free key at: https://aistudio.google.com

### 3. Run the server

```bash
python main.py
```

Then open: **http://127.0.0.1:8000**

---

## API

All detection endpoints are available at `http://127.0.0.1:8000/api/`

Interactive docs: `http://127.0.0.1:8000/api/docs`

---

## Tech Stack

| Layer    | Technology         |
|----------|--------------------|
| Backend  | Python + FastAPI   |
| AI Brain | Google Gemini API  |
| Scraping | httpx + BeautifulSoup |
| Database | SQLite             |
| Frontend | HTML + CSS + JS    |

---

## License

MIT License — free to use, modify, and distribute.

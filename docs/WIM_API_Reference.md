# Introduce WIM API
*A Comprehensive Utility & AI Forensics API for Your Application*

Welcome to the WIM (Why It's Messy) API! 

At WIM, we are passionate about providing developers with a clean, ad-free, and highly functional set of tools. This API service is crafted for developers who seek to integrate state-of-the-art AI content detection, secure ephemeral file transfers, and image/PDF manipulation directly into their applications.

Designed for a broad range of applications, the WIM API uses advanced Gemini AI models to analyze content credibility and provides rapid utility endpoints to handle everyday file tasks. Whether you are building a moderation bot, a secure file drop, or an automated image optimizer, the WIM API is here to help you achieve your vision.

Happy building! 🛠️

---

## How To Get an API Key?
To access the secured AI Detection endpoints of the WIM API, you must obtain an API key from our platform. 

*Note: File Transfer and Utility endpoints are currently open and do not require authentication.*

To generate your key, please run the internal key generation script:
`python -c "from backend.database.db import generate_api_key; print(generate_api_key('your_app_name'))"`

---

## Quick Start

To generate an AI analysis report via the API, you simply need to make a single POST request to our detection endpoints. 

Here is a sample code snippet to get you started on analyzing plain text for AI-generated content.

### Construct the request
Suppose you want to analyze a block of text to see if it was written by AI. Your API request should look like this:

#### Node.js
```javascript
const axios = require("axios");

const apiKey = "<YOUR-API-KEY>";
const url = "http://127.0.0.1:8000/api/detect/text";

const formData = new URLSearchParams();
formData.append("text", "The quick brown fox jumps over the lazy dog. This is a sample text to test the AI detection capabilities.");
formData.append("detection_type", "ai_content");

axios.post(url, formData, {
  headers: {
    "x-api-key": apiKey,
    "Content-Type": "application/x-www-form-urlencoded"
  }
})
.then(response => {
  console.log("Analysis Score:", response.data.score);
  console.log("Verdict:", response.data.verdict);
})
.catch(error => console.error("Error:", error.message));
```

#### Python
```python
import requests

api_key = "<YOUR-API-KEY>"
url = "http://127.0.0.1:8000/api/detect/text"

payload = {
    "text": "The quick brown fox jumps over the lazy dog. This is a sample text to test the AI detection capabilities.",
    "detection_type": "ai_content"
}
headers = {
    "x-api-key": api_key
}

response = requests.post(url, data=payload, headers=headers)
print("Analysis Score:", response.json().get("score"))
print("Verdict:", response.json().get("verdict"))
```

---

## Core Endpoints Detailed

### 1. Text Analysis
Submit plain text to the AI for deep forensic analysis.

**POST** `/api/detect/text`

#### Headers
- **x-api-key** (string, Required): `your-api-key`
- **Content-Type** (string, Required): `application/x-www-form-urlencoded`

#### Request Body
- **text** (string, Required): The content to analyze. Must be at least 20 characters.
- **detection_type** (string, Required): The type of analysis to run. Valid options: `ai_content`, `plagiarism`, `fake_news`, `fake_review`, `fake_profile`, `fake_job`, `phishing`, `code_plagiarism`.

#### Responses
`response.data` returns a detailed JSON object:
```json
{
  "id": 42,
  "detection_type": "ai_content",
  "score": 85,
  "verdict": "Likely AI Generated",
  "confidence": "High",
  "language": "English",
  "granularity": "span-level",
  "evidence": ["This is a sample text to test..."],
  "breakdown": {
    "ai_patterns_found": 3,
    "human_patterns_found": 1,
    "sentence_uniformity": 80,
    "vocabulary_diversity": 40
  },
  "raw_analysis": "The text exhibits highly uniform sentence structure typical of LLMs."
}
```

---

### 2. Secure File Transfer (Upload)
Upload a file to the ephemeral secure transfer system.

**POST** `/api/transfer/upload`

#### Request Body
- **file** (file, Required): The binary file to upload (multipart/form-data).

#### Responses
Returns the 6-digit access code for the file.
```json
{
  "code": "847291",
  "expires_in": "10 minutes",
  "file_name": "document.pdf"
}
```

---

### 3. Secure File Transfer (Download)
Retrieve a securely transferred file using its 6-digit code.

**GET** `/api/transfer/download/{code}`

#### Responses
- **200 OK**: Initiates a binary file download.
- **404 Not Found**: Thrown if the code is invalid or the 10-minute expiration window has passed.

---

### 4. Delete Transfer (Kill Switch)
Manually destroy a file before its 10-minute expiration.

**DELETE** `/api/transfer/delete/{code}`

#### Responses
```json
{
  "status": "deleted"
}
```

---

### 5. Image Compression
Compress an image dynamically.

**POST** `/api/utils/compress-image`

#### Request Body
- **file** (file, Required): The image file.
- **quality** (integer, Optional): The JPEG compression quality (1-100). Default is 85.

#### Responses
- **200 OK**: Returns the compressed binary image file.

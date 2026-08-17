# Product Requirements Document (PRD)
**Product Name:** Why It's Messy (WIM)
**Document Version:** 1.0
**Last Updated:** August 2026

## 1. Product Overview
**Why It's Messy (WIM)** is a radically free, open-source, and aesthetically premium multi-tool platform. It consolidates four major digital utility categories—AI/Fake Detection, PDF Manipulation, Image Compression, and Secure File Transfer—into one beautifully designed, cohesive ecosystem.

The product aims to replace the fragmented, ad-riddled, and visually unappealing utility websites (like standard PDF converters or size fixers) with an "artistic and designer-centric" experience that is a pleasure to look at and use.

## 2. Target Audience
- **Students & Academics:** Needing to compress documents for portal uploads, check for plagiarism/AI content, and merge/split PDFs.
- **Designers & Creatives:** Seeking a visually pleasing toolset without intrusive ads, dark patterns, or generic corporate themes.
- **Founders & Job Seekers:** Utilizing the "Project Idea Check" or "Fake Job Detection" tools to navigate the modern digital landscape safely.
- **Everyday Users:** Anyone who needs to quickly transfer a file securely (via a 6-digit code) or fix an image format without downloading dedicated software.

## 3. Core Features & Tool Suites

### 3.1 AI Forensics & Detection Suite
A comprehensive suite powered by Google's Gemini AI to verify digital authenticity.
- **Supported Inputs:** Text, URL scraping, and File Uploads (.txt, .pdf, .docx).
- **Detection Types:**
  - AI Content Detection
  - Plagiarism Check
  - Fake News & Misinformation Verification
  - Fake Review Detection
  - Fake Profile / Bot Identification
  - Scam Job Listing Detection
  - Phishing Email Detection
  - Code Plagiarism
  - Project Idea Check (Market Saturation & Pivot Suggestions)
- **Results Engine:** Provides a 0-100% credibility score, a verdict, a detailed 2-3 sentence analysis, and granular evidence (highlighted text spans) identifying exact triggers.

### 3.2 PDF Suite
A full-featured PDF manipulation toolkit.
- **Features:** Merge, Split, Compress, PDF to Word, PDF to Image, Image to PDF, Protect (Add Password), Unlock, Rotate, Add Watermark.
- **UX Highlights:** Interactive modal for each tool, live file queue with individual removal capabilities ("✕" button), and a "Clear All" batch action.

### 3.3 Size & Format Fixer
An intelligent compression and format conversion tool designed to bypass strict web-form upload limits.
- **Automatic Mode:** Target form presets (e.g., "Passport Photo < 200KB", "Generic Student Portal < 500KB") that automatically adjust compression ratios.
- **Manual Mode:** Granular pixel width and height adjustment.
- **UX Highlights:** Live thumbnail generation for uploaded images, dynamic UI toggling, and post-compression data savings feedback.

### 3.4 Send Anywhere (File Transfer)
A secure, ephemeral file-sharing system.
- **Workflow:** User drops a file → Receives an instant 6-digit code → Receiver enters the 6-digit code → File downloads securely.
- **Security & Ephemerality:** Files expire and are wiped from the server automatically after 10 minutes.
- **Kill Switch:** Senders have a "Delete Transfer" button to manually nuke the file from the server immediately after uploading if they change their mind.
- **Staged Uploads:** Users can review the selected file before confirming the upload.

## 4. Design Language & UX Guidelines
- **Theme:** Exclusively Light Mode. Warm cream canvas backgrounds with glassmorphism (translucent) cards.
- **Typography:** *Instrument Serif* (Italics) for elegant, editorial headers, paired with *Plus Jakarta Sans* for clean, legible body text.
- **Colors:** Vibrant accents used sparingly—Plum (`#6B4E71`), Crimson (`#E5322D`), Cobalt (`#2563EB`), Emerald (`#059669`).
- **User Forgiveness:** High emphasis on reversible actions (e.g., removing a file from a batch queue, cancelling a staged upload, or killing a live transfer). No aggressive modals or floating elements that block navigation.

## 5. Technical Architecture
- **Frontend:** Vanilla HTML, CSS, and JavaScript. No heavy frontend frameworks (React/Vue) to ensure lightning-fast loads. Custom CSS custom properties (variables) for theme management.
- **Backend:** Python with **FastAPI**.
- **Database:** SQLite (local file-based storage, optimized for ephemeral/lightweight tracking).
- **AI Integration:** Google `google-genai` SDK using `gemini-flash-latest`. Implements round-robin API key rotation and exponential backoff to handle rate limits and `503` high-demand errors smoothly.
- **Utilities:** `PyMuPDF` (fitz) and `pypdf` for document manipulation; `Pillow` for image resizing and compression; `BeautifulSoup4` for URL scraping.

## 6. Future Scope
- **User Accounts:** Allow users to save their scan history securely to the cloud.
- **Advanced PDF Editing:** In-browser annotations, signing, and text redaction without server trips (WebAssembly).
- **Peer-to-Peer Transfer:** Upgrade "Send Anywhere" to use WebRTC for large files to bypass server storage entirely.

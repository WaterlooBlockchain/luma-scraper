# 🎟️ luma-scraper

A CLI tool to log into your [Luma](https://lu.ma) account, fetch all your event guest lists, and extract attendee email addresses into a CSV.

Useful for organizers who want a quick export of attendee data from multiple events.

---

## 📦 Features

* ✅ Secure OTP-based login (no password stored)
* ✅ Automatically scrapes all events you manage
* ✅ Downloads CSVs of guest lists
* ✅ Extracts and saves only email addresses
* ✅ Handles Cloudflare rate limiting gracefully
* ✅ Retry failed events via recovery mode

---

## ⚙️ Setup

### 1. Clone this repo

```bash
git clone https://github.com/WaterlooBlockchain/luma-scraper.git
cd luma-scraper
```

### 2. Install dependencies

Make sure you’re using Python 3.10 or higher.

```bash
pip install -r requirements.txt
```

### 3. Set up your environment

Create a `.env` file in the root folder:

```env
EMAIL=you@example.com
```
---

## 🚀 Usage

Run the scraper from the terminal:

```bash
python main.py
```

You’ll be prompted with two modes:

* **Mode 1**: Fetch emails from all events you manage
* **Mode 2**: Retry previously failed events (saved in `failed.txt`)

After selecting Mode 1, you'll receive a one-time password (OTP) in your email. Enter it to log in.

Extracted emails will be saved to:

```
guests.csv
```

---

## 📂 Output Example

A sample `guests.csv` file will look like:

```csv
john@example.com
jane@domain.org
```

---

## 🔁 Handling Cloudflare Blocks

If Luma rate-limits your request:

* The blocked `event_api_id` will be saved to `failed.txt`
* Rerun the script in **Mode 2** later to retry those events

---

## 🧼 Good Practices

* Only scrape events that **you manage** — this tool is for authorized use only
* Always respect [Luma’s Terms of Service](https://lu.ma/terms)

---

## 📄 License

MIT — Free to use, modify, and distribute.

---

## 🤝 Contributing

Suggestions, ideas, or improvements are welcome.
Feel free to open an issue or submit a pull request!

---

# SmartReceipt-AI-Extractor

SmartReceipt-AI-Extractor is a production-ready automation tool designed for business owners and accountants. It monitors a local folder for receipts and invoices (JPG, PNG, PDF), uses OpenAI's GPT-4o (Vision) to extract key financial data, and automatically exports the organized data to a local CSV file and a Google Sheets document.

## 🚀 Why It Saves Businesses Time
Manual data entry of physical or digital receipts is prone to human error, tedious, and consumes valuable hours every week.
- **Batch Processing**: Drop 100 receipts in a folder and let the script do the work.
- **Accurate Intelligence**: GPT-4o Vision understands context, separating taxes from subtotals automatically.
- **Instant Validation**: The script double-checks math logic (`Total == Subtotal + Tax`) and flags anomalies automatically.
- **Cloud Sync**: By exporting directly to Google Sheets in real-time, accounting teams always have up-to-date ledgers without lifting a finger.

## ⚙️ Features
- **Auto-Monitoring**: Watches an `input/` folder and processes files as they arrive.
- **OpenAI Vision Integration**: Extracts Date, Vendor Name, Category, Subtotal, Tax, Total, and Currency.
- **Data Validation**: Ensures the math adds up.
- **Dual Export**: Saves locally to a CSV (`data_log.csv`) and remotely via Google Sheets API.
- **Error Handling**: Skips unreadable files, logs errors to `errors.log`, and moves successful files to a `processed/` folder.

## 📋 Prerequisites

Before installing the project, make sure you have the following:

| Requirement | Details |
|---|---|
| **Python** | 3.10 or higher |
| **OpenAI API Key** | With GPT-4o access. Get one at [platform.openai.com](https://platform.openai.com/api-keys) |
| **Poppler** | **Required only for PDF processing.** See [installation instructions](#installing-poppler) below |
| **Google Service Account** | *Optional.* Only needed if you want to export to Google Sheets |

### Installing Poppler

Poppler is required by `pdf2image` to convert PDF files into images. If you only process image files (JPG/PNG), you can skip this.

- **Windows**: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases), extract, and add the `bin/` folder to your system `PATH`.
- **macOS**: `brew install poppler`
- **Linux (Debian/Ubuntu)**: `sudo apt-get install poppler-utils`

### Google Sheets Setup (Optional)

If you want to automatically push extracted data to Google Sheets:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project (or use an existing one).
2. Enable the **Google Sheets API**.
3. Create a **Service Account** under *APIs & Services > Credentials*.
4. Download the JSON key file and save it as `credentials.json` in the project root.
5. Share your target Google Sheet with the service account email (found in the JSON file under `client_email`), granting **Editor** access.

## 🛠️ Installation

1. **Clone or Download the Repository**
   ```bash
   git clone https://github.com/Eguiguremsdev/SmartReceipt-AI-Extractor.git
   cd SmartReceipt-AI-Extractor
   ```

2. **Set Up a Virtual Environment (Recommended)**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables Configuration**
   Copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env     # macOS/Linux
   copy .env.example .env   # Windows
   ```
   Open `.env` and fill in your details:

   | Variable | Required | Description |
   |---|---|---|
   | `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API Key with GPT-4o access |
   | `GOOGLE_CREDENTIALS_FILE` | ❌ Optional | Path to your Google Service Account JSON file (default: `credentials.json`) |
   | `GOOGLE_SPREADSHEET_ID` | ❌ Optional | The ID from your Google Sheet URL: `https://docs.google.com/spreadsheets/d/<THIS_IS_THE_ID>/edit` |
   | `GOOGLE_SHEET_NAME` | ❌ Optional | The worksheet tab name (default: `Sheet1`) |
   | `INPUT_DIR` | ❌ Optional | Folder to monitor for new receipts (default: `input`) |
   | `PROCESSED_DIR` | ❌ Optional | Folder for processed files (default: `processed`) |

## 📖 How to Use

1. **Start the Extractor**
   Run the main script to start monitoring the `input/` folder:
   ```bash
   python main.py
   ```

2. **Add Files**
   Drag and drop your images (JPG/PNG) or PDFs of receipts into the `input/` directory.

3. **Review Data**
   - Wait a few seconds for processing to finish.
   - Check your local `data_log.csv` or navigate to your connected Google Sheet to see the extracted data.
   - Processed files are automatically moved to the `processed/` folder to prevent duplicates.
   - If a file failed, check `errors.log` for details.

## 📁 Project Structure

```
SmartReceipt-AI-Extractor/
├── config.py          # Loads and validates environment variables
├── main.py            # Entry point — monitors input folder and orchestrates processing
├── processor.py       # Sends images to OpenAI GPT-4o Vision and extracts data
├── exporter.py        # Exports data to CSV and Google Sheets
├── utils.py           # Image encoding, PDF conversion, and file utilities
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore         # Files excluded from Git
├── input/             # Drop receipts here (monitored by the script)
└── processed/         # Successfully processed files are moved here
```

## 🤝 Contributing
Contributions are welcome. Please open an issue or submit a pull request!

## 📄 License
This project is open source and available under the [MIT License](LICENSE).

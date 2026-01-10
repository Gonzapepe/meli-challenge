# PII Classification & Anonymization

LangGraph-based solution for detecting, classifying, and anonymizing sensitive information according to **GDPR**, **HIPAA**, and **PCI DSS** regulations.

## 🎯 Features

- **Multi-Regulation Support**: Automatic detection and classification for GDPR, HIPAA, and PCI DSS compliance
- **Hybrid Entity Detection**: Combines regex patterns and LLM-based detection for maximum accuracy
- **Smart Anonymization**: Context-aware replacement with malformed token prevention
- **RAG-Enhanced Classification**: Uses vector database with regulation documents for justification
- **Quality Assurance**: Built-in validation to ensure anonymization quality
- **Audit Logging**: Complete SQLite-based tracking of all processing activities

## 📋 Requirements

- **Python**: 3.10 or higher
- **API Keys**:
  - [Groq API Key](https://console.groq.com) (for LLM inference)
  - [Voyage AI API Key](https://www.voyageai.com) (for embeddings)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd challenge-meli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required:
#   - GROQ_API_KEY=your_groq_api_key_here
#   - VOYAGE_API_KEY=your_voyage_api_key_here
```

### 3. Database Setup

**Automatic Setup**
```bash
# Databases initialize automatically on first run
python main.py --process-all
```

This sets up:
- **SQLite database**: Stores audit logs and regulation rules
- **Vector database (ChromaDB)**: Indexed GDPR, HIPAA, and PCI DSS documents

> **Note**: Setup runs only once. If databases exist, they won't be recreated.  

## 💻 Usage

### Process All Test Texts

```bash
python main.py --process-all
```

### Process a Single Text

```bash
# Auto-detect regulation
python main.py --input data/test_texts/texto1.txt

# Specify regulation
python main.py --input data/test_texts/texto1.txt --regulation GDPR

# With verbose output
python main.py --input data/test_texts/texto2.txt --regulation HIPAA --verbose
```

### CLI Options

| Option | Shorthand | Description |
|--------|-----------|-------------|
| `--input` | `-i` | Path to input text file |
| `--regulation` | `-r` | Target regulation: `GDPR`, `HIPAA`, `PCI_DSS`, or `AUTO` (default) |
| `--process-all` | - | Process all texts in `data/test_texts/` |
| `--output-dir` | `-o` | Custom output directory (default: `outputs/`) |
| `--verbose` | `-v` | Enable detailed logging |

### Example Commands

```bash
# Process all texts with verbose output
python main.py --process-all --verbose

# Process specific file with auto-detection
python main.py -i data/test_texts/texto3.txt

# Process with HIPAA compliance
python main.py -i data/test_texts/texto4.txt -r HIPAA -v

# Custom output directory
python main.py --process-all -o custom_outputs/
```

## 📁 Project Structure

```
challenge-meli/
├── data/
│   ├── test_texts/           # Sample input texts
│   ├── vector_db/            # ChromaDB vector database
│   └── audit.db # SQLite audit database
├── docs/                     # Documentation files
├── outputs/
│   ├── results.json          # Structured processing results
│   ├── results.md            # Human-readable justifications
│   └── logs/                 # Application logs
├── scripts/
│   ├── setup_databases.py    # Main setup script
│   ├── setup_sqlite_db.py    # SQLite initialization
│   └── setup_vector_db.py    # Vector DB initialization
├── src/
│   ├── anonymization/        # Anonymization techniques
│   ├── database/             # Database managers (SQLite & Vector)
│   ├── detection/            # Entity detection (Regex & LLM)
│   ├── graph/                # LangGraph workflow nodes
│   │   └── nodes/            # Individual node implementations
│   ├── llm/                  # LLM client (Groq wrapper)
│   ├── schemas/              # Pydantic data models
│   ├── utils/                # Utilities (logging, formatting, validation)
│   └── config.py             # Configuration settings
├── tests/                    # Test files
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── .gitignore                # Git ignore rules
```

## 📄 Outputs

After processing, results are saved in the `outputs/` directory:

### `results.json`
Structured JSON with:
- Entity details (type, sensitivity level, regulations)
- Anonymized text
- Processing metadata
- Justification citations

### `results.md`
Human-readable markdown with:
- Original vs. anonymized text comparison
- Entity-by-entity transformation justifications
- Regulatory citations from vector database

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [architecture.md](docs/architecture.md) | LangGraph workflow and system design |
| [AUTO_SETUP_IMPLEMENTATION.md](docs/AUTO_SETUP_IMPLEMENTATION.md) | Automatic setup feature details |
| [fixes_implemented.md](docs/fixes_implemented.md) | Recent bug fixes and improvements |

## 🔧 Advanced Configuration

Edit `.env` to customize:

```bash
# Model configuration
LLM_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Database paths
VECTOR_DB_PATH=data/vector_db
SQLITE_DB_PATH=data/audit.db
```

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset databases (WARNING: deletes all data)
rm data/audit.db
rm -rf data/vector_db/
python scripts/setup_databases.py
```

### API Rate Limits
If you encounter rate limit errors with Voyage AI:
- The setup script includes automatic retry logic with 30-second delays
- For large document sets, setup may take several minutes

## 📝 License

This project was developed as part of the Mercado Libre AI Challenge.

---

**Need help?** Check the [docs/](docs/) folder for detailed guides.

# Setup and Database Management

This document explains how the automatic setup system works and how to manage the application's databases.

## Automatic Setup

The application now **automatically checks and runs setup** when you first run `main.py`. You don't need to manually run setup scripts unless you want to rebuild the databases.

### How It Works

When you run the main application, it will:

1. **Check if databases exist**:
   - SQLite database at `data/audit.db`
   - Vector database at `data/vector_db/`

2. **Run setup automatically if needed**:
   - If databases don't exist, setup runs automatically
   - Initializes SQLite with regulation rules
   - Populates vector DB with regulation documents
   - This only happens **once** on first run

3. **Skip setup on subsequent runs**:
   - If databases exist, setup is skipped
   - Application starts immediately

### First Run

```bash
# Just run the main application
python main.py --process-all

# On first run, you'll see:
# 🚀 INITIAL SETUP REQUIRED
# Running database setup (this may take a few minutes)...
# ... setup output ...
# ✅ Database setup complete!
# ... then your normal processing starts ...
```

### Subsequent Runs

```bash
# On subsequent runs, setup is skipped
python main.py --process-all

# You'll see:
# (setup check happens silently)
# ... processing starts immediately ...
```

## Manual Database Management

### Check Database Status

To inspect what's in your databases:

```bash
python scripts/check_databases.py
```

This shows:
- Vector DB collections and document counts
- SQLite statistics and recent logs
- Whether setup is needed

### Rebuild Databases

If you need to rebuild the databases from scratch:

```bash
# Delete the databases
rm -rf data/audit.db data/vector_db/

# Then run main again (setup will run automatically)
python main.py --process-all
```

Or run setup manually:

```bash
# Run the master setup script
python scripts/setup_databases.py
```

### Setup Individual Databases

You can also set up databases individually:

```bash
# SQLite only
python scripts/setup_sqlite_db.py

# Vector DB only (takes ~1 minute due to rate limiting)
python scripts/setup_vector_db.py
```

## How Idempotency Works

All setup scripts are **idempotent** - safe to run multiple times:

### SQLite Setup
- Checks if database already has data
- If data exists, updates rules but skips test data
- If empty, performs full population

### Vector DB Setup
- Checks if collections already exist
- If 3+ collections exist, skips re-population
- To force rebuild, delete the `data/vector_db/` folder

## Setup Components

### 1. SQLite Database (`data/audit.db`)

Contains:
- **processing_logs**: Audit trail of all entity processing
- **regulation_rules**: Entity type → anonymization technique mappings
- **processing_sessions**: Session tracking for reporting

Populated with:
- 20+ predefined regulation rules for GDPR, HIPAA, and PCI DSS
- Test session and log entry

### 2. Vector Database (`data/vector_db/`)

Contains three ChromaDB collections:
- **gdpr**: 10 GDPR regulation documents
- **hipaa**: 8 HIPAA regulation documents
- **pci_dss**: 7 PCI DSS regulation documents

Uses:
- Voyage AI embeddings (`voyage-3-large`)
- Semantic search for regulation lookup

## Troubleshooting

### Setup Fails on First Run

If automatic setup fails:

1. Check your `.env` file has `GROQ_API_KEY`
2. Check internet connection (needed for embeddings)
3. Look at error messages for specific issues
4. Try manual setup: `python scripts/setup_databases.py`

### Databases Corrupt or Inconsistent

Delete and rebuild:

```bash
rm -rf data/audit.db data/vector_db/
python main.py --process-all
```

### Want to Reset Just One Database

```bash
# Reset SQLite only
rm data/audit.db
python scripts/setup_sqlite_db.py

# Reset Vector DB only
rm -rf data/vector_db/
python scripts/setup_vector_db.py
```

## Configuration

Database paths can be configured in `.env` (optional):

```env
# Vector database location (defaults to data/vector_db)
VECTOR_DB_PATH=data/vector_db

# SQLite is always at data/audit.db
```

## Setup Checker Module

The automatic setup uses `src/utils/setup_checker.py`:

- `is_setup_complete()`: Check if both databases exist
- `run_setup_if_needed()`: Run setup only if needed
- `get_setup_status()`: Get detailed status info

You can import and use these in your own scripts:

```python
from src.utils.setup_checker import is_setup_complete, run_setup_if_needed

# Check status
if is_setup_complete():
    print("Ready to go!")

# Or just run setup if needed
run_setup_if_needed()
```

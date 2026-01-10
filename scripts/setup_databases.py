"""Master setup script to initialize both databases."""

import sys
from pathlib import Path
import traceback
from scripts.setup_sqlite_db import setup_sqlite_db

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Run all setup scripts."""
    print("=" * 70)
    print(" PII CLASSIFICATION SYSTEM - DATABASE SETUP")
    print("=" * 70)
    print()
    
    print("  Checking environment configuration...")
    try:
        from src.config import config
        config.validate()
        print("   Groq API key configured")
        print(f"   LLM Model: {config.LLM_MODEL}")
        print(f"   Embedding Model: {config.EMBEDDING_MODEL}")
    except ValueError as e:
        print(f"   Configuration error: {e}")
        print("\n Make sure you have a .env file with GROQ_API_KEY set")
        return 1
    except Exception as e:
        print(f"   Unexpected error: {e}")
        return 1
    
    print("  Setting up SQLite database (audit logs & rules)...")
    print("-" * 70)
    try:
        
        setup_sqlite_db()
    except Exception as e:
        print(f"\n SQLite setup failed: {e}")
        traceback.print_exc()
        return 1
    
    print()
    print()
    
    print("  Setting up Vector database (regulation documents)...")
    print("-" * 70)
    try:
        from scripts.setup_vector_db import populate_vector_db
        populate_vector_db()
    except Exception as e:
        print(f"\n Vector DB setup failed: {e}")
        traceback.print_exc()
        return 1
    
    print()
    print("=" * 70)
    print("✨ DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("📊 Summary:")
    print("  SQLite database initialized")
    print("     - Processing logs table")
    print("     - Regulation rules table")
    print("     - Processing sessions table")
    print()
    print("  Vector database initialized")
    print("     - GDPR regulation documents")
    print("     - HIPAA regulation documents")
    print("     - PCI DSS regulation documents")
    print()
    print(" Next steps:")
    print("  1. Process test texts: python main.py --process-all")
    print("  2. Or single text: python main.py --input data/test_texts/texto1.txt --regulation GDPR")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

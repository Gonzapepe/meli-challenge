from pathlib import Path
from typing import Tuple
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from scripts.setup_databases import main as setup_main

from src.config import config
from src.utils.logger import logger


def check_databases_exist() -> Tuple[bool, bool]:
    """
    Check if both SQLite and Vector databases exist.
    
    Returns:
        Tuple[bool, bool]: (sqlite_exists, vector_db_exists)
    """
    sqlite_path = config.DATA_DIR / "audit.db"
    sqlite_exists = sqlite_path.exists()
    
    vector_db_path = config.VECTOR_DB_PATH
    vector_db_exists = vector_db_path.exists() and vector_db_path.is_dir()
    
    if vector_db_exists:
        chroma_db = vector_db_path / "chroma.sqlite3"
        vector_db_exists = chroma_db.exists()
    
    return sqlite_exists, vector_db_exists


def is_setup_complete() -> bool:
    """
    Check if full database setup is complete.
    
    Returns:
        bool: True if both databases are set up, False otherwise
    """
    sqlite_exists, vector_db_exists = check_databases_exist()
    return sqlite_exists and vector_db_exists


def run_setup_if_needed() -> bool:
    """
    Check if databases exist and run setup if needed.
    
    Returns:
        bool: True if setup was run, False if databases already exist
    """
    sqlite_exists, vector_db_exists = check_databases_exist()
    
    if sqlite_exists and vector_db_exists:
        logger.debug("✓ Databases already initialized")
        return False
    
    logger.info("=" * 70)
    logger.info("🚀 INITIAL SETUP REQUIRED")
    logger.info("=" * 70)
    
    if not sqlite_exists:
        logger.info("  ⚠️  SQLite database not found")
    else:
        logger.info("  ✓ SQLite database exists")
    
    if not vector_db_exists:
        logger.info("  ⚠️  Vector database not found")
    else:
        logger.info("  ✓ Vector database exists")
    
    logger.info("")
    logger.info("Running database setup (this may take a few minutes)...")
    logger.info("")
    
    try:
        result = setup_main()
        
        if result != 0:
            logger.error("❌ Database setup failed!")
            return False
        
        logger.info("✅ Database setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_setup_status() -> dict:
    """
    Get detailed setup status information.
    
    Returns:
        dict: Status information about database setup
    """
    sqlite_exists, vector_db_exists = check_databases_exist()
    
    sqlite_path = config.DATA_DIR / "audit.db"
    vector_db_path = config.VECTOR_DB_PATH
    
    status = {
        "setup_complete": sqlite_exists and vector_db_exists,
        "sqlite": {
            "exists": sqlite_exists,
            "path": str(sqlite_path),
            "size_bytes": sqlite_path.stat().st_size if sqlite_exists else 0
        },
        "vector_db": {
            "exists": vector_db_exists,
            "path": str(vector_db_path),
            "is_directory": vector_db_path.is_dir() if vector_db_path.exists() else False
        }
    }
    
    return status

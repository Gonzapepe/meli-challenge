#!/usr/bin/env python3

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.vector_db_manager import VectorDBManager
from src.database.sqlite_manager import SQLiteManager
from src.config import config


def check_vector_db():
    """Check vector database status and contents."""
    print("=" * 70)
    print("📊 VECTOR DATABASE STATUS")
    print("=" * 70)
    
    vector_db_path = config.VECTOR_DB_PATH
    print(f"\n📁 Location: {vector_db_path}")
    
    if not vector_db_path.exists():
        print("❌ Vector DB directory does not exist!")
        print("   Run: python scripts/setup_vector_db.py")
        return
    
    files_in_db = list(vector_db_path.glob("*"))
    if len(files_in_db) <= 1: 
        print("⚠️  Vector DB is EMPTY!")
        print("   Run: python scripts/setup_vector_db.py")
        return
    
    try:
        vector_db = VectorDBManager()
        collections = vector_db.list_collections()
        
        print(f"\n✅ Vector DB is initialized")
        print(f"📚 Collections: {len(collections)}")
        
        for collection_name in collections:
            stats = vector_db.get_collection_stats(collection_name)
            print(f"\n  📖 {collection_name.upper()}:")
            print(f"     Documents: {stats['count']}")
        
        print("\n🔍 Testing semantic search...")
        print("-" * 70)
        test_query = "email"
        results = vector_db.query_regulations(test_query, n_results=2)
        
        print(f"Query: 'How should {test_query} be protected?'")
        for i, result in enumerate(results[:2], 1):
            print(f"\n  {i}. [{result['regulation']}] (distance: {result['distance']:.4f})")
            print(f"     {result['document'][:150]}...")
        
    except Exception as e:
        print(f"\n❌ Error accessing vector DB: {e}")
        import traceback
        traceback.print_exc()


def check_sqlite_db():
    """Check SQLite database status and contents."""
    print("\n\n" + "=" * 70)
    print("💾 SQLITE DATABASE STATUS")
    print("=" * 70)
    
    sqlite_path = config.DATA_DIR / "audit.db"
    print(f"\n📁 Location: {sqlite_path}")
    
    if not sqlite_path.exists():
        print("⚠️  SQLite database does not exist yet!")
        print("   It will be created automatically when you process texts.")
        return
    
    try:
        sqlite_manager = SQLiteManager()
        stats = sqlite_manager.get_statistics()
        
        print(f"\n✅ Database exists")
        print(f"\n📊 Statistics:")
        print(f"  Total logs: {stats['total_logs']}")
        print(f"  Total sessions: {stats['total_sessions']}")
        
        if stats['entities_by_type']:
            print(f"\n  📋 Entities Detected by Type:")
            for entity in stats['entities_by_type'][:10]:  # Top 10
                print(f"     - {entity['entity_type']}: {entity['count']}")
        
        if stats['regulations_applied']:
            print(f"\n  ⚖️  Regulations Applied:")
            for reg in stats['regulations_applied']:
                print(f"     - {reg['applicable_regulations']}: {reg['count']}")
        
        print("\n📝 Recent Processing Logs (last 5):")
        print("-" * 70)
        report = sqlite_manager.generate_compliance_report()
        
        for i, log in enumerate(report[:5], 1):
            print(f"\n  {i}. Text: {log['text_id']} | Type: {log['entity_type']}")
            print(f"     Entity: {log['detected_entity']}")
            print(f"     Technique: {log['applied_technique']}")
            print(f"     Timestamp: {log['timestamp']}")
        
    except Exception as e:
        print(f"\n❌ Error accessing SQLite DB: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("\n🔍 DATABASE INSPECTION TOOL")
    print("=" * 70)
    
    check_vector_db()
    check_sqlite_db()
    
    print("\n\n" + "=" * 70)
    print("✨ Inspection complete!")
    print("=" * 70)
    
    print("\n💡 Tips:")
    print("  - To populate Vector DB: python scripts/setup_vector_db.py")
    print("  - To query SQLite: python scripts/check_databases.py")
    print("  - To view SQLite directly: sqlite3 data/audit.db")


if __name__ == "__main__":
    main()

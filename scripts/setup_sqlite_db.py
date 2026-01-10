import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.sqlite_manager import SQLiteManager
from src.config import config


REGULATION_RULES = [
    {
        "entity_type": "person_name",
        "regulation": "GDPR",
        "article_citation": "Art. 4(5)",
        "required_technique": "pseudonymization",
        "sensitivity_level": "high",
        "description": "Names are direct identifiers requiring pseudonymization per GDPR Art. 4(5)"
    },
    {
        "entity_type": "email",
        "regulation": "GDPR",
        "article_citation": "Art. 32(1)(a)",
        "required_technique": "masking",
        "sensitivity_level": "high",
        "description": "Email addresses should be masked to protect personal data while maintaining domain for analysis"
    },
    {
        "entity_type": "phone",
        "regulation": "GDPR",
        "article_citation": "Art. 4(1)",
        "required_technique": "masking",
        "sensitivity_level": "medium",
        "description": "Phone numbers are personal data, mask middle digits while preserving country code"
    },
    {
        "entity_type": "address",
        "regulation": "GDPR",
        "article_citation": "Art. 5(1)(c)",
        "required_technique": "generalization",
        "sensitivity_level": "high",
        "description": "Addresses should be generalized to city/region level per data minimization principle"
    },
    {
        "entity_type": "national_id",
        "regulation": "GDPR",
        "article_citation": "Art. 32(1)(a)",
        "required_technique": "tokenization",
        "sensitivity_level": "critical",
        "description": "National IDs require strong protection through tokenization or hashing"
    },
    {
        "entity_type": "date_of_birth",
        "regulation": "GDPR",
        "article_citation": "Art. 5(1)(c)",
        "required_technique": "generalization",
        "sensitivity_level": "medium",
        "description": "Birth dates should be generalized to year only unless full date is essential"
    },
    
    {
        "entity_type": "patient_name",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(i)",
        "required_technique": "removal",
        "sensitivity_level": "critical",
        "description": "Patient names are Safe Harbor identifier #1 and must be completely removed"
    },
    {
        "entity_type": "physician_name",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(i)",
        "required_technique": "removal",
        "sensitivity_level": "high",
        "description": "Healthcare provider names are Safe Harbor identifier #1 and must be removed"
    },
    {
        "entity_type": "email",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(vi)",
        "required_technique": "removal",
        "sensitivity_level": "high",
        "description": "Email addresses are Safe Harbor identifier #6 and must be completely removed"
    },
    {
        "entity_type": "phone",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(iv)",
        "required_technique": "removal",
        "sensitivity_level": "high",
        "description": "Telephone numbers are Safe Harbor identifier #4 and must be removed"
    },
    {
        "entity_type": "date",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(iii)",
        "required_technique": "generalization",
        "sensitivity_level": "medium",
        "description": "All date elements except year must be removed per Safe Harbor method"
    },
    {
        "entity_type": "address",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)(ii)",
        "required_technique": "removal",
        "sensitivity_level": "high",
        "description": "Geographic subdivisions smaller than state must be removed"
    },
    {
        "entity_type": "diagnosis",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)",
        "required_technique": "keep",
        "sensitivity_level": "low",
        "description": "Medical diagnoses are NOT direct identifiers and may be retained for clinical research"
    },
    {
        "entity_type": "medication",
        "regulation": "HIPAA",
        "article_citation": "§164.514(b)(2)",
        "required_technique": "keep",
        "sensitivity_level": "low",
        "description": "Medication information is NOT a direct identifier under Safe Harbor"
    },
    
    {
        "entity_type": "credit_card",
        "regulation": "PCI DSS",
        "article_citation": "Req. 3.3",
        "required_technique": "truncation",
        "sensitivity_level": "critical",
        "description": "PAN must be masked/truncated showing only last 4 digits"
    },
    {
        "entity_type": "cvv",
        "regulation": "PCI DSS",
        "article_citation": "Req. 3.2",
        "required_technique": "removal",
        "sensitivity_level": "critical",
        "description": "CVV/CVC must NEVER be stored after authorization and must be removed"
    },
    {
        "entity_type": "expiration_date",
        "regulation": "PCI DSS",
        "article_citation": "Req. 3.4",
        "required_technique": "tokenization",
        "sensitivity_level": "high",
        "description": "Expiration dates should be tokenized if stored"
    },
    {
        "entity_type": "cardholder_name",
        "regulation": "PCI DSS",
        "article_citation": "Req. 3.4",
        "required_technique": "pseudonymization",
        "sensitivity_level": "high",
        "description": "Cardholder names require protection through pseudonymization or encryption"
    },
    
    # Combined PCI + GDPR Rules
    {
        "entity_type": "credit_card",
        "regulation": "PCI DSS + GDPR",
        "article_citation": "PCI Req. 3.3 + GDPR Art. 32",
        "required_technique": "truncation_tokenization",
        "sensitivity_level": "critical",
        "description": "Apply strictest requirements: PCI truncation with GDPR security measures"
    },
    {
        "entity_type": "cardholder_name",
        "regulation": "PCI DSS + GDPR",
        "article_citation": "PCI Req. 3.4 + GDPR Art. 4(5)",
        "required_technique": "pseudonymization",
        "sensitivity_level": "high",
        "description": "Use GDPR pseudonymization which satisfies both regulations"
    },
    {
        "entity_type": "email",
        "regulation": "PCI DSS + GDPR",
        "article_citation": "GDPR Art. 32",
        "required_technique": "masking",
        "sensitivity_level": "high",
        "description": "Email follows GDPR rules as PCI DSS doesn't directly regulate email addresses"
    }
]


def setup_sqlite_db():
    """Initialize SQLite database and populate with regulation rules."""
    print("🚀 Initializing SQLite Database...")
    
    db = SQLiteManager()
    
    print(f"📁 Database location: {db.db_path}")
    
    stats = db.get_statistics()
    if stats['total_logs'] > 0 or len(stats.get('entities_by_type', [])) > 0:
        print("\n✓ Database already populated with data. Skipping re-population.")
        print(f"  - Existing processing logs: {stats['total_logs']}")
        print(f"  - Existing sessions: {stats['total_sessions']}")
        
        rules_updated = 0
        for rule in REGULATION_RULES:
            try:
                db.add_regulation_rule(
                    entity_type=rule["entity_type"],
                    regulation=rule["regulation"],
                    required_technique=rule["required_technique"],
                    article_citation=rule.get("article_citation"),
                    sensitivity_level=rule.get("sensitivity_level"),
                    description=rule.get("description")
                )
                rules_updated += 1
            except Exception as e:
                print(f"  ✗ Error updating rule for {rule['entity_type']}: {e}")
        
        print(f"✅ Updated {rules_updated} regulation rules")
        return

    rules_added = 0
    
    for rule in REGULATION_RULES:
        try:
            db.add_regulation_rule(
                entity_type=rule["entity_type"],
                regulation=rule["regulation"],
                required_technique=rule["required_technique"],
                article_citation=rule.get("article_citation"),
                sensitivity_level=rule.get("sensitivity_level"),
                description=rule.get("description")
            )
            rules_added += 1
            print(f"  ✓ {rule['entity_type']} ({rule['regulation']}): {rule['required_technique']}")
        except Exception as e:
            print(f"  ✗ Error adding rule for {rule['entity_type']}: {e}")
    
    print(f"\n✅ Added {rules_added} regulation rules")
    
    # Test queries
    print("\n🔍 Testing rule lookups...")
    print("-" * 60)
    
    test_cases = [
        ("credit_card", "PCI DSS"),
        ("email", "GDPR"),
        ("patient_name", "HIPAA"),
        ("credit_card", "PCI DSS + GDPR")
    ]
    
    for entity_type, regulation in test_cases:
        rule = db.get_regulation_rule(entity_type, regulation)
        if rule:
            print(f"\n✓ {entity_type} + {regulation}:")
            print(f"  Technique: {rule['required_technique']}")
            print(f"  Citation: {rule['article_citation']}")
            print(f"  Sensitivity: {rule['sensitivity_level']}")
        else:
            print(f"\n✗ No rule found for {entity_type} + {regulation}")
    
    # Show statistics
    print("\n📊 Database Statistics:")
    print("=" * 60)
    stats = db.get_statistics()
    print(f"  Total processing logs: {stats['total_logs']}")
    print(f"  Total sessions: {stats['total_sessions']}")
    print(f"  Regulation rules: {rules_added}")
    
    # Create a test session and log
    print("\n🧪 Creating test session and log entry...")
    session_id = "test_session_001"
    db.create_session(
        session_id=session_id,
        text_id="test_text_1",
        primary_regulation="GDPR"
    )
    
    log_id = db.log_entity_processing(
        text_id="test_text_1",
        detected_entity="test@example.com",
        entity_type="email",
        applied_technique="masking",
        sensitivity_level="high",
        applicable_regulations="GDPR",
        justification="Test entry for email masking per GDPR Art. 32",
        confidence_score=0.95,
        original_value="test@example.com",
        anonymized_value="t***t@example.com"
    )
    
    print(f"  ✓ Created session: {session_id}")
    print(f"  ✓ Created log entry: {log_id}")
    
    # Update session
    db.update_session(
        session_id=session_id,
        status="completed",
        total_entities_detected=1,
        total_entities_anonymized=1,
        quality_check_passed=True
    )
    
    print(f"  ✓ Updated session status")
    
    # Retrieve session logs
    logs = db.get_session_logs(session_id)
    print(f"\n📋 Retrieved {len(logs)} log entries for session {session_id}")
    
    print("\n✨ SQLite database setup complete!")
    print(f"📍 Database file: {db.db_path}")
    print("\n💡 Database Tables Created:")
    print("  1. processing_logs - Audit trail of all entity processing")
    print("  2. regulation_rules - Direct mappings for entity types → techniques")
    print("  3. processing_sessions - Session tracking for reporting")


if __name__ == "__main__":
    try:
        setup_sqlite_db()
    except Exception as e:
        print(f"\n❌ Error setting up SQLite database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

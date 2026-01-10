"""Setup script to initialize and populate the vector database with regulation documents."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.vector_db_manager import VectorDBManager
from src.config import config

GDPR_DOCUMENTS = [
    {
        "text": "Article 4(1) GDPR: 'Personal data' means any information relating to an identified or identifiable natural person ('data subject'); an identifiable natural person is one who can be identified, directly or indirectly, in particular by reference to an identifier such as a name, an identification number, location data, an online identifier or to one or more factors specific to the physical, physiological, genetic, mental, economic, cultural or social identity of that natural person.",
        "metadata": {"article": "4(1)", "topic": "definition_personal_data", "category": "definitions"}
    },
    {
        "text": "Article 4(5) GDPR: 'Pseudonymisation' means the processing of personal data in such a manner that the personal data can no longer be attributed to a specific data subject without the use of additional information, provided that such additional information is kept separately and is subject to technical and organisational measures to ensure that the personal data are not attributed to an identified or identifiable natural person.",
        "metadata": {"article": "4(5)", "topic": "pseudonymisation", "category": "definitions"}
    },
    {
        "text": "Article 5(1)(c) GDPR - Data Minimization: Personal data shall be adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed. This principle requires that only the minimum amount of personal data necessary for each specific purpose should be processed.",
        "metadata": {"article": "5(1)(c)", "topic": "data_minimization", "category": "principles"}
    },
    {
        "text": "Article 32(1)(a) GDPR - Security of Processing: Taking into account the state of the art, the costs of implementation and the nature, scope, context and purposes of processing as well as the risk of varying likelihood and severity for the rights and freedoms of natural persons, the controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including the pseudonymisation and encryption of personal data.",
        "metadata": {"article": "32(1)(a)", "topic": "security_measures", "category": "security"}
    },
    {
        "text": "GDPR Email Protection: Email addresses are considered personal data under Article 4(1) as they can directly identify an individual. Protection measures should include masking, pseudonymization, or tokenization depending on the use case. The domain part may be preserved for analytical purposes while protecting the local part.",
        "metadata": {"entity_type": "email", "topic": "email_protection", "category": "entity_specific"}
    },
    {
        "text": "GDPR Name Protection: Full names (first name, last name) are direct identifiers under Article 4(1). Pseudonymization (Art. 4(5)) is the recommended technique, replacing names with unique identifiers like 'Subject-001'. This enables data utility while preventing direct identification.",
        "metadata": {"entity_type": "person_name", "topic": "name_protection", "category": "entity_specific"}
    },
    {
        "text": "GDPR Date of Birth: Birth dates are personal data. Under data minimization (Art. 5(1)(c)), generalization to year only is often sufficient for demographic analysis while reducing identification risk. Full dates should only be retained when strictly necessary.",
        "metadata": {"entity_type": "date_of_birth", "topic": "date_protection", "category": "entity_specific"}
    },
    {
        "text": "GDPR Address Protection: Full addresses are highly identifying. Generalization to city/region level maintains geographical utility while protecting privacy. Street-level details should be removed unless essential for the processing purpose.",
        "metadata": {"entity_type": "address", "topic": "address_protection", "category": "entity_specific"}
    },
    {
        "text": "GDPR Phone Number Protection: Phone numbers are direct identifiers. Masking techniques should preserve country code and last few digits for statistical purposes while obscuring the identifying middle digits. Format: +56 9 ****5555.",
        "metadata": {"entity_type": "phone", "topic": "phone_protection", "category": "entity_specific"}
    },
    {
        "text": "GDPR National ID Protection: National identification numbers (SSN, RUT, etc.) are high-sensitivity personal data requiring strong protection. Tokenization with secure, irreversible hashing is recommended for most use cases, enabling referential integrity without exposing the actual identifier.",
        "metadata": {"entity_type": "national_id", "topic": "national_id_protection", "category": "entity_specific"}
    }
]

HIPAA_DOCUMENTS = [
    {
        "text": "HIPAA Safe Harbor Method §164.514(b)(2): The following identifiers of the individual or of relatives, employers, or household members of the individual must be removed: (1) Names; (2) All geographic subdivisions smaller than a State; (3) All elements of dates (except year) for dates directly related to an individual; (4) Telephone numbers; (5) Fax numbers; (6) Electronic mail addresses; (7) Social security numbers; (8) Medical record numbers; (9) Health plan beneficiary numbers; (10) Account numbers; (11) Certificate/license numbers; (12) Vehicle identifiers and serial numbers; (13) Device identifiers and serial numbers; (14) Web Universal Resource Locators (URLs); (15) Internet Protocol (IP) address numbers; (16) Biometric identifiers; (17) Full-face photographic images; (18) Any other unique identifying number, characteristic, or code.",
        "metadata": {"section": "164.514(b)(2)", "topic": "safe_harbor_identifiers", "category": "deidentification"}
    },
    {
        "text": "HIPAA Patient Name Removal: Under Safe Harbor method, all names (first, last, middle, maiden) of the patient, relatives, employers, and household members must be completely removed. Use generic placeholders like [PATIENT] or [REDACTED] rather than pseudonyms to ensure compliance.",
        "metadata": {"entity_type": "patient_name", "topic": "name_removal", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Physician/Provider Name Removal: Healthcare provider names are Safe Harbor identifier #1. All physician names, nurse names, and other healthcare worker names must be removed from de-identified datasets. Use role-based placeholders like [PHYSICIAN] or [HEALTHCARE_PROVIDER].",
        "metadata": {"entity_type": "physician_name", "topic": "provider_name_removal", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Date Restrictions: Under Safe Harbor §164.514(b)(2)(iii), all elements of dates (except year) directly related to an individual must be removed. This includes birth dates, admission dates, discharge dates, service dates, and death dates. Only the year may be retained. Dates must be generalized to year only: '2024-03-15' → '2024'.",
        "metadata": {"entity_type": "date", "topic": "date_generalization", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Email Removal: Email addresses are Safe Harbor identifier #6. All electronic mail addresses must be completely removed from de-identified health information. No partial masking is permitted - complete removal with placeholder [EMAIL_REMOVED] is required.",
        "metadata": {"entity_type": "email", "topic": "email_removal", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Phone Number Removal: Telephone numbers are Safe Harbor identifier #4. All telephone numbers must be completely removed. Unlike GDPR where masking is acceptable, HIPAA Safe Harbor requires complete removal. Use placeholder [PHONE_REMOVED].",
        "metadata": {"entity_type": "phone", "topic": "phone_removal", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Medical Information: Clinical data such as diagnoses, conditions, medications, and procedures are NOT considered direct identifiers under HIPAA Safe Harbor. These may be retained in de-identified datasets as they are necessary for medical research and treatment analysis. Only remove if they represent unique identifying characteristics.",
        "metadata": {"entity_type": "diagnosis", "topic": "clinical_data_retention", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Address Removal: Geographic subdivisions smaller than a State must be removed (Safe Harbor identifier #2). Street addresses, cities, ZIP codes must all be removed. Only state-level or broader geographic information may be retained.",
        "metadata": {"entity_type": "address", "topic": "address_removal", "category": "entity_specific"}
    },
    {
        "text": "HIPAA Medical Record Numbers: Medical record numbers (MRN) are Safe Harbor identifier #8 and must be completely removed. These are unique patient identifiers and cannot be retained even in tokenized or hashed form in de-identified datasets.",
        "metadata": {"entity_type": "medical_record_number", "topic": "mrn_removal", "category": "entity_specific"}
    }
]

PCI_DSS_DOCUMENTS = [
    {
        "text": "PCI DSS Requirement 3.3: Mask PAN (Primary Account Number) when displayed. The first six and last four digits are the maximum number of digits to be displayed. This standard applies to all displays of cardholder data, including on payment card receipts, web pages, and screens.",
        "metadata": {"requirement": "3.3", "topic": "pan_masking", "category": "display_protection"}
    },
    {
        "text": "PCI DSS Requirement 3.4: Render PAN unreadable anywhere it is stored. Approved methods include: (1) One-way hashes based on strong cryptography; (2) Truncation (hashing cannot be used to replace the truncated segment of PAN); (3) Index tokens with securely stored pads; (4) Strong cryptography with associated key-management processes and procedures.",
        "metadata": {"requirement": "3.4", "topic": "pan_storage", "category": "storage_protection"}
    },
    {
        "text": "PCI DSS Credit Card Truncation: When displaying or storing Primary Account Numbers (PAN), show only the last 4 digits. Format: ************1111 or XXXX-XXXX-XXXX-1111. The first 6 digits (BIN/IIN) may be shown if needed for routing but should generally be masked for security.",
        "metadata": {"entity_type": "credit_card", "topic": "pan_truncation", "category": "entity_specific"}
    },
    {
        "text": "PCI DSS CVV/CVC Protection: Card Verification Values (CVV, CVV2, CVC, CVC2, CID) must NEVER be stored after authorization, even if encrypted. These values must be removed immediately after transaction completion. For de-identification, use complete removal with [CVV_REMOVED] placeholder.",
        "metadata": {"entity_type": "cvv", "topic": "cvv_prohibition", "category": "entity_specific"}
    },
    {
        "text": "PCI DSS Expiration Date: Card expiration dates are sensitive authentication data. While not explicitly prohibited from storage like CVV, they should be tokenized or encrypted if stored. For de-identification purposes, tokenization is recommended: '12/25' → 'TOKEN_EXP_a7b3c9'.",
        "metadata": {"entity_type": "expiration_date", "topic": "expiry_protection", "category": "entity_specific"}
    },
    {
        "text": "PCI DSS Cardholder Name: The cardholder name printed on the card is considered Cardholder Data and must be protected. Acceptable techniques include encryption, tokenization, or pseudonymization. Format: 'John Smith' → 'Cardholder-001' or tokenized reference.",
        "metadata": {"entity_type": "cardholder_name", "topic": "name_protection", "category": "entity_specific"}
    },
    {
        "text": "PCI DSS Tokenization Requirements: Tokens must be sufficiently different from the original PAN that they cannot be reverse-engineered to determine PAN. Tokens should use strong cryptographic algorithms. The tokenization system must ensure that tokens cannot be used to mathematically derive the original PAN value.",
        "metadata": {"topic": "tokenization_standards", "category": "techniques"}
    },
    {
        "text": "PCI DSS Combined with GDPR: When processing payment card data subject to both PCI DSS and GDPR, apply the strictest requirements. PAN must be truncated/tokenized per PCI DSS 3.3/3.4, while cardholder names can use GDPR pseudonymization. Email addresses should follow GDPR masking as PCI DSS doesn't directly regulate them.",
        "metadata": {"topic": "pci_gdpr_combined", "category": "combined_regulations"}
    }
]


def populate_vector_db():
    """Populate vector database with regulation documents."""
    import time
    
    print("🚀 Initializing Vector Database...")
    
    vector_db = VectorDBManager()
    
    print(f"📁 Vector DB location: {config.VECTOR_DB_PATH}")
    print(f"🤖 Embedding model: {config.EMBEDDING_MODEL}")
    
    existing_collections = vector_db.list_collections()
    if existing_collections and len(existing_collections) >= 3:
        print(f"\n✓ Vector database already populated with {len(existing_collections)} collections:")
        for collection_name in existing_collections:
            stats = vector_db.get_collection_stats(collection_name)
            print(f"  - {collection_name.upper()}: {stats['count']} documents")
        print("\nSkipping re-population. Delete the vector DB folder to rebuild.")
        return
    
    print(f"⏱️  Note: Adding documents one-by-one with 30s delays for free tier 3 RPM limit")
    total_docs = len(GDPR_DOCUMENTS) + len(HIPAA_DOCUMENTS) + len(PCI_DSS_DOCUMENTS)
    print(f"⏱️  Estimated time: ~{total_docs * 30 / 60:.1f} minutes")
    
    print("\n⚠️  Resetting existing vector database...")
    vector_db.reset_database()
    
    def add_docs_slowly(collection_name, documents):
        print(f"\n📚 Populating {collection_name.upper()} collection ({len(documents)} documents)...")
        for i, doc in enumerate(documents):
            try:
                vector_db.add_documents(
                    collection_name=collection_name,
                    documents=[doc["text"]],
                    metadatas=[doc["metadata"]],
                    ids=[f"{collection_name}_{i}"]
                )
                print(f"  ✅ Added document {i+1}/{len(documents)}")
                
                if i < len(documents) - 1:
                    print(f"     ⏳ Waiting 30 seconds...")
                    time.sleep(30)
            except Exception as e:
                print(f"  ❌ Error adding document {i+1}: {e}")
                if i < len(documents) - 1:
                    print(f"     ⏳ Waiting 30 seconds before retry...")
                    time.sleep(30)
        print(f"✅ Completed {collection_name.upper()} collection")
    
    add_docs_slowly("gdpr", GDPR_DOCUMENTS)
    print("\n⏳ Waiting 30 seconds before next collection...")
    time.sleep(30)
    
    add_docs_slowly("hipaa", HIPAA_DOCUMENTS)
    print("\n⏳ Waiting 30 seconds before next collection...")
    time.sleep(30)
    
    add_docs_slowly("pci_dss", PCI_DSS_DOCUMENTS)
    
    print("\n💾 Persisting vector database to disk...")
    vector_db.persist()
    
    print("\n📊 Vector Database Statistics:")
    print("=" * 60)
    for collection_name in vector_db.list_collections():
        stats = vector_db.get_collection_stats(collection_name)
        print(f"  {collection_name.upper()}: {stats['count']} documents")
    
    print("\n🔍 Testing semantic search...")
    print("-" * 60)
    test_query = "How should email addresses be protected?"
    results = vector_db.query_regulations("email", n_results=2)
    
    print(f"Query: '{test_query}'")
    print(f"\nTop Results:")
    for i, result in enumerate(results[:2], 1):
        print(f"\n{i}. [{result['regulation']}] (distance: {result['distance']:.4f})")
        print(f"   {result['document'][:200]}...")
    
    print("\n✨ Vector database setup complete!")
    print(f"📍 Data persisted to: {config.VECTOR_DB_PATH}")


if __name__ == "__main__":
    try:
        populate_vector_db()
    except Exception as e:
        print(f"\n❌ Error setting up vector database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

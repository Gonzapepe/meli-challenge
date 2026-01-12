
## Methodology Overview

### 1. **Detection Phase**
I thought of using a hybrid detection approach thanks to some data being easier to classify using regex based approaches (such as emails, phone numbers, etc.) and others being easier to classify using LLM based approaches (such as names, medical diagnoses, etc.):
- Regex-based detection For structured data (credit cards, dates, phone numbers, national IDs)
- LLM-based detection For contextual entities (names, medical diagnoses, procedures, medications)
- Vector similarity search To retrieve relevant regulation examples

### 2. **Classification Phase**
Each text is analyzed to determine the applicable regulation based on:
- Entity types present: Medical data -> HIPAA, payment data -> PCI DSS, general personal data -> GDPR. The go to is GDPR
- Context analysis Understanding the domain and purpose of the data
- Evaluating the sensitivity and potential impact of data exposure

### 3. **Anonymization Phase**
Techniques are selected based on:
- Regulatory requirements: Each regulation mandates specific protection levels
- Entity sensitivity: Critical, high, medium, or low
- Data utility: Balancing protection with usability
- Re-identification risk: Minimizing the potential to reconstruct original data

## Graph Nodes Justification

### 1. **Ingest Node**
- Used for text preprocessing and entity detection
- This is the entry point that transforms raw text into structured data. It implements the hybrid detection approach (regex + LLM) that forms the foundation of the system.
- What it does:
  - Normalizes input text
  - Runs regex-based detection for structured datta
  - Runs LLM-based detection for contextual entities
  - Merges both detection results, prioritizing regex for overlaps (since it's more deterministic)

### 2. **Classify Node**
- Used for entity classification and regulation determination
- Different entities require different protection levels. This node assigns sensitivity levels and determines which regulations apply.
- What it does:
  - Uses a quick classification dictionary for known entity types (email, phone, credit_card, etc.)
  - Falls back to LLM for unknown or ambiguous entity types
  - Aggregates regulation flags based on entity types
  - Determines the primary (most restrictive) regulation using priority logic:
    - PCI DSS Only if actual payment card data (credit_card or CVV) is detected
    - HIPAA If medical data present without payment data
    - GDPR Default/fallback for general personal data

### 3. **Route Node**
- Workflow bifurcation based on regulation
- This implements the required bifurcation. Different regulations need different processing paths.
- What it does:
  - Routes to `justify_gdpr`, `justify_hipaa`, or `justify_pci` nodes based on the primary regulation
  - Handles edge cases (e.g., PCI+GDPR dual compliance, escalation for unknown cases)

### 4. **Justify Node**
- Generate detailed justifications for anonymization decisions
- What it does:
  - For each detected entity, retrieves the appropriate anonymization strategy based on entity type and regulation
  - Generates regulation-specific citations
  - Uses LLM to create detailed, professional justifications explaining why each technique was chosen
  - Builds the anonymization strategy map for the next node

### 5. **Anonymize Node**
- Apply anonymization techniques to the original text
- This is where we are transforming the input text into a privacy-compliant output
- What it does:
  - Applies the anonymization strategies determined by the justify node
  - Implements 6 techniques:
    - Removal
    - Truncation
    - Tokenization
    - Pseudonymization
    - Masking
    - Generalization
  - Maintains a transformation log for audit trail
  - Handles entity overlaps and sorting to ensure correct replacement order
- Processing entities from right to left prevents offset issues when replacing text

### 6. **Quality Check Node**
- Validate that no sensitive data leaked through
- What it does:
  - Re-runs regex detection on the anonymized output to catch any patterns that shouldn't be there
  - Filters false positives
  - Checks that original entity values aren't still present unless intentionally kept like clinical data that does not need to be anonymized
  - Uses LLM as a final sanity check for residual PII
  - Returns issues found for review
- Multiple validations (regex + original value check + LLM) provide additional security.

### 7. **Retry Logic**
- Allow up to 2 retries if quality check fails
- What it does:
  - If quality check passes → route to END
  - If quality check fails and retry_count < MAX_RETRIES → route back to anonymize node
  - If max retries reached → route to END with quality_passed = False

## Technique Selection Rationale

### **Removal**
- Only used for critical data that must not be stored in HIPAA contexts

### **Tokenization**
- Only used for high-sensitivity data in payment contexts (expiry dates, medical records in PCI context)

### **Pseudonymization**
- Only used for names and identifiers in GDPR contexts where data linkage may be needed

### **Masking**
- Only used for email addresses where domain information is relevant

### **Generalization**
- Only used for dates, addresses, ZIP codes with medium sensitivity

### **Keep**
- Only used for clinical data (diagnoses, medications) that cannot identify individuals alone
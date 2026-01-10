#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.graph.workflow import run_workflow
from src.utils.output_formatter import save_results
from src.utils.logger import logger
from src.utils.setup_checker import run_setup_if_needed


def main():
    parser = argparse.ArgumentParser(
        description="PII Classification & Anonymization using LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --process-all
  python main.py --input data/test_texts/texto1.txt --regulation GDPR
  python main.py --input data/test_texts/texto2.txt --regulation HIPAA
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to input text file"
    )
    
    parser.add_argument(
        "--regulation", "-r",
        type=str,
        choices=["GDPR", "HIPAA", "PCI_DSS", "AUTO"],
        default="AUTO",
        help="Target regulation (default: AUTO-detect)"
    )
    
    parser.add_argument(
        "--process-all",
        action="store_true",
        help="Process all test texts in data/test_texts/"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=None,
        help="Output directory (default: outputs/)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if not args.input and not args.process_all:
        parser.error("Either --input or --process-all is required")
    
    run_setup_if_needed()
    
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please copy .env.example to .env and add your GROQ_API_KEY")
        sys.exit(1)
    
    output_dir = Path(args.output_dir) if args.output_dir else config.OUTPUTS_DIR
    
    if args.process_all:
        results = process_all_texts(args.verbose)
    else:
        results = process_single_text(args.input, args.regulation, args.verbose)
    
    if results:
        json_path, md_path = save_results(results, output_dir)
        logger.info(f"Results saved to:")
        logger.info(f"  - {json_path}")
        logger.info(f"  - {md_path}")
    else:
        logger.warning("No results to save")


def process_all_texts(verbose: bool = False) -> list:
    """Process all texts in the test_texts directory."""
    test_dir = config.TEST_TEXTS_DIR
    
    if not test_dir.exists():
        logger.error(f"Test texts directory not found: {test_dir}")
        return []
    
    text_files = sorted(test_dir.glob("*.txt"))
    
    if not text_files:
        logger.warning(f"No .txt files found in {test_dir}")
        return []
    
    logger.info(f"Processing {len(text_files)} text files...")
    
    results = []
    for text_file in text_files:
        text_id = text_file.stem
        logger.info(f"Processing {text_id}...")
        
        try:
            text = text_file.read_text(encoding="utf-8")
            state = run_workflow(text, text_id)
            results.append(state)
            
            if verbose:
                logger.info(f"  - Entities detected: {len(state.get('classified_entities', []))}")
                logger.info(f"  - Primary regulation: {state.get('primary_regulation')}")
                logger.info(f"  - Quality passed: {state.get('quality_passed')}")
        
        except Exception as e:
            logger.error(f"Error processing {text_id}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
    
    logger.info(f"Processed {len(results)}/{len(text_files)} files successfully")
    return results


def process_single_text(input_path: str, regulation: str, verbose: bool = False) -> list:
    """Process a single text file."""
    text_file = Path(input_path)
    
    if not text_file.exists():
        logger.error(f"Input file not found: {text_file}")
        return []
    
    text_id = text_file.stem
    logger.info(f"Processing {text_id}...")
    
    try:
        text = text_file.read_text(encoding="utf-8")
        state = run_workflow(text, text_id)
        
        if verbose:
            logger.info(f"Entities detected: {len(state.get('classified_entities', []))}")
            logger.info(f"Primary regulation: {state.get('primary_regulation')}")
            logger.info(f"Processing time: {state.get('processing_time_ms')}ms")
        
        return [state]
    
    except Exception as e:
        logger.error(f"Error processing {text_id}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return []


if __name__ == "__main__":
    main()

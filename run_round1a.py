#!/usr/bin/env python3
"""
Runner script for Round 1A - PDF Outline Extraction
"""

import os
import sys
from pathlib import Path
from round1a_outline_extractor import process_round1a

def main():
    """Main function to run Round 1A"""
    # Default directories
    input_dir = "input"
    output_dir = "output"
    
    # Check if custom directories are provided
    if len(sys.argv) >= 2:
        input_dir = sys.argv[1]
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    
    # Validate input directory
    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' does not exist!")
        print("Please create the directory and add PDF files to process.")
        sys.exit(1)
    
    # Check for PDF files
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in '{input_dir}'!")
        print("Please add PDF files to the input directory.")
        sys.exit(1)
    
    print(f"🔍 Found {len(pdf_files)} PDF file(s) to process:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    print(f"\n📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    
    # Process PDFs
    print("\n🚀 Starting Round 1A processing...")
    process_round1a(input_dir, output_dir)
    
    print("\n✅ Round 1A processing complete!")
    print(f"Check the '{output_dir}' directory for JSON output files.")

if __name__ == "__main__":
    main()

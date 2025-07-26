import fitz  # PyMuPDF
import json
import re
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import Counter

class PDFOutlineExtractor:
    """
    Extracts a hierarchical outline from a PDF file by analyzing font styles and text patterns.
    
    The process involves:
    1. Identifying the main body text style to establish a baseline.
    2. Detecting headings as text with larger or bolder fonts than the body text.
    3. Determining heading levels (H1, H2, etc.) based on the relative sizes of heading fonts.
    4. Building a nested, hierarchical JSON structure from the identified headings.
    """

    def __init__(self):
        # More specific regex patterns to reduce false positives
        self.heading_patterns = [
            r'^(Chapter|Section)\s+\d+[:\.\s].*$',      # "Chapter 1", "Section 2.1"
            r'^\d+(\.\d+)*\s+.*$',                      # "1. Introduction", "2.1. Methods"
        ]

    def _cleanup_text(self, text: str) -> str:
        """Removes extra whitespace and cleans up text."""
        return re.sub(r'\s+', ' ', text).strip()

    def extract_title(self, doc: fitz.Document) -> str:
        """Extracts the document title from the first page, looking for the largest text."""
        if not doc or len(doc) == 0:
            return "Untitled Document"

        first_page = doc[0]
        # Extract text blocks, sorted by vertical position then horizontal
        blocks = sorted(first_page.get_text("dict")["blocks"], key=lambda b: (b['bbox'][1], b['bbox'][0]))

        max_font_size = 0.0
        title_candidates = []

        # Find the largest font size on the page
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > max_font_size:
                            max_font_size = span["size"]
        
        # Collect all text with the largest font size
        if max_font_size > 0:
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Allow for minor floating point variations
                            if abs(span["size"] - max_font_size) < 0.1:
                                text = self._cleanup_text(span["text"])
                                if text:
                                    title_candidates.append(text)

        if title_candidates:
            return " ".join(title_candidates)

        return "Untitled Document"

    def _get_text_spans(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extracts all text spans from the document with their properties."""
        spans = []
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = self._cleanup_text(span["text"])
                            if text:
                                spans.append({
                                    "text": text,
                                    "font_size": round(span["size"], 2),
                                    "font": span["font"],
                                    "is_bold": "bold" in span["font"].lower(),
                                    "page": page_num + 1,
                                })
        return spans

    def _get_body_text_style(self, spans: List[Dict[str, Any]]) -> Tuple[float, str]:
        """Determines the most common font size and style, presumed to be the body text."""
        if not spans:
            return 12.0, "" # Default values

        font_styles = [(s["font_size"], s["font"]) for s in spans]
        # Use Counter to find the most common style tuple
        most_common_style = Counter(font_styles).most_common(1)
        
        if most_common_style:
            return most_common_style[0][0]
        
        return 12.0, ""

    def _is_heading(self, span: Dict[str, Any], body_font_size: float) -> bool:
        """Determines if a text span is likely a heading."""
        text = span["text"]
        font_size = span["font_size"]
        is_bold = span["is_bold"]

        # Basic filtering
        if len(text) < 3 or len(text) > 250:
            return False
        if text.endswith('.') or text.endswith(':'): # Likely part of a sentence
            text = text[:-1]
        
        # Style-based checks
        is_larger = font_size > body_font_size * 1.15
        if is_larger or is_bold:
            # Check for heading-like patterns
            for pattern in self.heading_patterns:
                if re.match(pattern, text):
                    return True
            # Title case check (avoid flagging all capitalized words at start of sentence)
            if text.istitle() and len(text.split()) > 1 and len(text.split()) < 10:
                return True
            # All caps check
            if text.isupper() and len(text.split()) > 1 and len(text.split()) < 10:
                return True

        return False

    def _assign_heading_levels(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assigns H1, H2, etc., based on font sizes of identified headings."""
        if not headings:
            return []

        # Get unique font sizes from headings, sorted in descending order
        heading_font_sizes = sorted(list(set([h["font_size"] for h in headings])), reverse=True)
        
        size_to_level = {size: f"H{i+1}" for i, size in enumerate(heading_font_sizes)}

        for heading in headings:
            heading["level"] = size_to_level.get(heading["font_size"], "H9") # Default to a high number
        
        return headings

    def _build_hierarchical_outline(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Builds a nested dictionary structure from a flat list of headings."""
        if not headings:
            return []

        outline = []
        # A list to keep track of the current parent heading at each level
        path = []

        for heading in headings:
            level_num = int(heading["level"][1:])
            
            # Go back up the hierarchy to the correct parent level
            while len(path) >= level_num:
                path.pop()

            # Prepare the new heading node
            heading_node = {
                "level": heading["level"],
                "text": heading["text"],
                "page": heading["page"],
                "children": []
            }

            if not path:
                # This is a top-level heading (H1)
                outline.append(heading_node)
            else:
                # This is a sub-heading, append it to its parent's children
                parent = path[-1]
                parent["children"].append(heading_node)
            
            # Add current heading to the path for subsequent children
            path.append(heading_node)
        
        return outline

    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Main function to extract a structured, hierarchical outline from a PDF."""
        try:
            doc = fitz.open(pdf_path)
            
            # 1. Extract title
            title = self.extract_title(doc)
            
            # 2. Get all text spans
            all_spans = self._get_text_spans(doc)
            if not all_spans:
                doc.close()
                return {"title": title, "outline": []}
            
            # 3. Determine body text style to use as a baseline
            body_font_size, _ = self._get_body_text_style(all_spans)

            # 4. Identify all potential headings
            headings = [span for span in all_spans if self._is_heading(span, body_font_size)]

            # 5. Assign levels (H1, H2, ...) to headings
            leveled_headings = self._assign_heading_levels(headings)
            
            # 6. Build the final hierarchical structure
            hierarchical_outline = self._build_hierarchical_outline(leveled_headings)

            doc.close()
            
            return {"title": title, "outline": hierarchical_outline}
        
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return {"title": "Error Processing Document", "outline": []}


def process_pdfs(input_dir: str, output_dir: str):
    """Processes all PDFs in an input directory and saves their outlines to an output directory."""
    extractor = PDFOutlineExtractor()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for pdf_file in input_path.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        
        outline_data = extractor.extract_outline(str(pdf_file))
        
        output_file = output_path / f"{pdf_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(outline_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved outline to {output_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python your_script_name.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir_arg = sys.argv[1]
    output_dir_arg = sys.argv[2]
    
    process_pdfs(input_dir_arg, output_dir_arg)
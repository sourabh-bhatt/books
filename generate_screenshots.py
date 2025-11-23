#!/usr/bin/env python3
"""
PDF Screenshot Generator with Claude Vision Integration

This script converts each page of a PDF to screenshots and uses Claude Vision API
to analyze the content of each page.
"""

import os
import sys
import base64
from pathlib import Path
from typing import List, Dict, Optional
import json

import fitz  # PyMuPDF
from PIL import Image
from anthropic import Anthropic
from dotenv import load_dotenv


class PDFScreenshotGenerator:
    """Generate screenshots from PDF pages and analyze with Claude Vision."""

    def __init__(self, pdf_path: str, output_dir: str = "screenshots", dpi: int = 150):
        """
        Initialize the PDF screenshot generator.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save screenshots
            dpi: DPI for rendering (higher = better quality but larger files)
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF standard DPI is 72

        # Load environment variables
        load_dotenv()

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
            print("Vision analysis will be skipped. Set ANTHROPIC_API_KEY to enable it.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def generate_screenshots(self) -> List[Path]:
        """
        Convert each page of the PDF to a screenshot.

        Returns:
            List of paths to generated screenshot files
        """
        print(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        screenshot_paths = []

        print(f"Total pages: {len(doc)}")

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Render page to image
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Save as PNG
            output_path = self.output_dir / f"page_{page_num + 1:03d}.png"
            pix.save(output_path)
            screenshot_paths.append(output_path)

            print(f"✓ Generated screenshot: {output_path.name}")

        doc.close()
        print(f"\n✓ Generated {len(screenshot_paths)} screenshots in '{self.output_dir}/'")

        return screenshot_paths

    def encode_image(self, image_path: Path) -> str:
        """
        Encode image to base64 string.

        Args:
            image_path: Path to the image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def analyze_screenshot_with_vision(
        self,
        image_path: Path,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Analyze a screenshot using Claude Vision API.

        Args:
            image_path: Path to the screenshot
            prompt: Custom prompt for analysis (optional)

        Returns:
            Dictionary containing analysis results
        """
        if not self.client:
            return {
                "page": image_path.stem,
                "analysis": "Skipped - No API key",
                "error": "ANTHROPIC_API_KEY not set"
            }

        # Default prompt if none provided
        if prompt is None:
            prompt = """Analyze this page and provide:
1. A brief description of the page content
2. Main topics or headings
3. Key information or takeaways
4. Any notable images, diagrams, or charts

Be concise but informative."""

        try:
            # Encode image
            image_data = self.encode_image(image_path)

            # Call Claude Vision API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            return {
                "page": image_path.stem,
                "analysis": message.content[0].text,
                "model": message.model,
                "tokens_used": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "page": image_path.stem,
                "analysis": None,
                "error": str(e)
            }

    def analyze_all_screenshots(
        self,
        screenshot_paths: List[Path],
        custom_prompt: Optional[str] = None
    ) -> List[Dict]:
        """
        Analyze all screenshots using Claude Vision.

        Args:
            screenshot_paths: List of paths to screenshots
            custom_prompt: Custom prompt for analysis

        Returns:
            List of analysis results
        """
        if not self.client:
            print("\n⚠ Skipping Vision analysis - ANTHROPIC_API_KEY not set")
            return []

        print("\n" + "="*70)
        print("Analyzing screenshots with Claude Vision API")
        print("="*70 + "\n")

        results = []
        total = len(screenshot_paths)

        for idx, image_path in enumerate(screenshot_paths, 1):
            print(f"Analyzing {image_path.name} ({idx}/{total})...")
            result = self.analyze_screenshot_with_vision(image_path, custom_prompt)
            results.append(result)

            if "error" in result:
                print(f"  ✗ Error: {result['error']}")
            else:
                print(f"  ✓ Analysis complete")

        return results

    def save_analysis_report(self, results: List[Dict], output_file: str = "analysis_report.json"):
        """
        Save analysis results to a JSON file.

        Args:
            results: List of analysis results
            output_file: Output filename
        """
        output_path = self.output_dir / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Analysis report saved to: {output_path}")

        # Also create a readable markdown report
        md_path = self.output_dir / "analysis_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# PDF Analysis Report\n\n")
            f.write(f"**Source PDF:** {self.pdf_path.name}\n\n")
            f.write(f"**Total Pages:** {len(results)}\n\n")
            f.write("---\n\n")

            for result in results:
                page_name = result.get('page', 'Unknown')
                f.write(f"## {page_name}\n\n")

                if 'error' in result:
                    f.write(f"**Error:** {result['error']}\n\n")
                else:
                    f.write(f"{result.get('analysis', 'No analysis available')}\n\n")

                    if 'tokens_used' in result:
                        tokens = result['tokens_used']
                        f.write(f"*Tokens - Input: {tokens['input']}, Output: {tokens['output']}*\n\n")

                f.write("---\n\n")

        print(f"✓ Markdown report saved to: {md_path}")


def main():
    """Main function to run the screenshot generator."""

    # Configuration
    PDF_FILE = "Book.pdf"
    OUTPUT_DIR = "screenshots"
    DPI = 150  # Adjust for quality (150-300 recommended)

    # Check if PDF exists
    if not Path(PDF_FILE).exists():
        print(f"Error: PDF file '{PDF_FILE}' not found!")
        sys.exit(1)

    # Create generator
    generator = PDFScreenshotGenerator(
        pdf_path=PDF_FILE,
        output_dir=OUTPUT_DIR,
        dpi=DPI
    )

    # Generate screenshots
    print("\n" + "="*70)
    print("PDF Screenshot Generator with Claude Vision")
    print("="*70 + "\n")

    screenshot_paths = generator.generate_screenshots()

    # Analyze with Claude Vision
    results = generator.analyze_all_screenshots(screenshot_paths)

    # Save report if we have results
    if results:
        generator.save_analysis_report(results)

    print("\n" + "="*70)
    print("✓ Process Complete!")
    print("="*70)
    print(f"\nScreenshots saved in: {OUTPUT_DIR}/")
    if results:
        print(f"Analysis reports: {OUTPUT_DIR}/analysis_report.json")
        print(f"                  {OUTPUT_DIR}/analysis_report.md")


if __name__ == "__main__":
    main()

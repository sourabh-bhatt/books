# Books - PDF Screenshot Generator with Claude Vision

A Python tool that converts PDF pages into screenshots and uses Claude's Vision API to analyze the content of each page.

## Features

- 📸 **Screenshot Generation**: Converts each PDF page to high-quality PNG images
- 🤖 **AI Analysis**: Uses Claude Vision API to analyze and describe page content
- 📊 **Detailed Reports**: Generates JSON and Markdown reports of the analysis
- ⚙️ **Configurable Quality**: Adjustable DPI for screenshot quality
- 🔍 **Comprehensive Analysis**: Extracts main topics, key information, and visual elements

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyMuPDF Pillow anthropic python-dotenv
```

### 2. Configure API Key

1. Get your Anthropic API key from [https://console.anthropic.com/](https://console.anthropic.com/)
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## Usage

### Basic Usage

Simply run the script to process `Book.pdf`:

```bash
python3 generate_screenshots.py
```

### What It Does

1. **Converts PDF pages to screenshots** - Each page is rendered as a high-quality PNG image
2. **Analyzes each page with Claude Vision** - AI analyzes the content, layout, and key information
3. **Generates reports** - Creates both JSON and Markdown reports with the analysis

### Output

The script creates a `screenshots/` directory containing:

- `page_001.png`, `page_002.png`, etc. - Screenshot images of each page
- `analysis_report.json` - Detailed JSON report with all analysis data
- `analysis_report.md` - Human-readable Markdown report

### Example Analysis

For each page, Claude Vision provides:

- Description of page content
- Main topics or headings
- Key information or takeaways
- Notable images, diagrams, or charts

## Configuration

You can modify these settings in `generate_screenshots.py`:

```python
PDF_FILE = "Book.pdf"       # PDF file to process
OUTPUT_DIR = "screenshots"  # Output directory
DPI = 150                   # Screenshot quality (150-300 recommended)
```

### DPI Settings Guide

- **150 DPI**: Good quality, smaller files (recommended for most use cases)
- **200 DPI**: High quality, balanced file size
- **300 DPI**: Maximum quality, larger files (for detailed diagrams/images)

## Running Without API Key

If you don't set an `ANTHROPIC_API_KEY`, the script will still:

✓ Generate all screenshots
✗ Skip the AI analysis

This is useful if you only need the screenshots.

## Advanced Usage

### Custom Analysis Prompt

Modify the `analyze_screenshot_with_vision` method to customize what Claude analyzes:

```python
custom_prompt = """
Focus on:
1. Technical diagrams and their explanations
2. Code snippets and examples
3. Important formulas or equations
"""

results = generator.analyze_all_screenshots(screenshot_paths, custom_prompt)
```

## Requirements

- Python 3.8+
- PyMuPDF (for PDF processing)
- Pillow (for image handling)
- Anthropic Python SDK (for Claude Vision API)
- python-dotenv (for environment variables)

## File Structure

```
.
├── Book.pdf                    # Your PDF file
├── generate_screenshots.py     # Main script
├── requirements.txt            # Python dependencies
├── .env.example               # Template for environment variables
├── .env                       # Your API key (not in git)
├── README.md                  # This file
└── screenshots/               # Generated output (not in git)
    ├── page_001.png
    ├── page_002.png
    ├── ...
    ├── analysis_report.json
    └── analysis_report.md
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

- Make sure you created a `.env` file (not `.env.example`)
- Verify your API key is correctly set in `.env`
- The `.env` file should be in the same directory as the script

### "PDF file not found"

- Ensure `Book.pdf` exists in the current directory
- Or modify `PDF_FILE` in the script to point to your PDF

### Low Quality Screenshots

- Increase the DPI value (try 200 or 300)
- Higher DPI = better quality but larger files

## Cost Considerations

Claude Vision API usage incurs costs based on:
- Number of images analyzed
- Image size
- Number of tokens in the response

Each page analysis typically uses:
- ~1500-2000 input tokens (for a standard page screenshot)
- ~300-500 output tokens (for the analysis text)

Check [Anthropic's pricing](https://www.anthropic.com/pricing) for current rates.

## License

This project is open source and available under the MIT License.

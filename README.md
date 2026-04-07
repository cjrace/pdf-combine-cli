# pdf-combine-cli

A simple Python CLI tool for combining multiple PDFs and images into a single PDF file.

Files are read from a dedicated input folder, merged in alphabetical order, and written to a single output PDF in the project root. Unsupported file types are flagged with a warning and skipped — they do not stop the tool from running.

**Supported input formats:** `.pdf`, `.png`, `.jpg`, `.jpeg`,

---

## Setup

**Requirements:** Python 3.8+

Install dependencies:
```
python -m pip install -r requirements.txt
```

## Usage

1. Place the files you want to combine into a folder named `to-combine` within the project root.

2. Run the script, providing your desired output filename as an argument:
   ```
   python combine.py example-output.pdf
   ```

3. The combined PDF will be saved in the project root.

**Notes:**
- Files are combined in alphabetical order by filename.
- If the output file already exists, you will be prompted to overwrite it, choose a new name, or abort.

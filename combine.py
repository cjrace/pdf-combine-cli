import argparse
import os
import sys
import tempfile

from PIL import Image
from pypdf import PdfWriter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "to-combine")

PDF_EXTS = {".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
SUPPORTED_EXTS = PDF_EXTS | IMAGE_EXTS


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combine all files in ./to-combine/ into a single PDF."
    )
    parser.add_argument(
        "output",
        help="Output PDF filename (e.g. output.pdf). Saved in the project root.",
    )
    return parser.parse_args()


def resolve_output_path(filename):
    if not filename.lower().endswith(".pdf"):
        print(f"[ERROR] Output filename must end in .pdf (got: {filename})")
        sys.exit(1)
    return os.path.join(SCRIPT_DIR, filename)


def prompt_output_collision(output_path):
    filename = os.path.basename(output_path)
    print(f"\n[WARN] '{filename}' already exists in the output directory.")
    while True:
        print("  [1] Overwrite")
        print("  [2] Save under a different name")
        print("  [3] Abort")
        choice = input("Choose an option (1/2/3): ").strip()
        if choice == "1":
            return output_path
        elif choice == "2":
            while True:
                new_name = input("Enter new filename (must end in .pdf): ").strip()
                if not new_name:
                    print("  [ERROR] Filename cannot be empty.")
                    continue
                if not new_name.lower().endswith(".pdf"):
                    print("  [ERROR] Filename must end in .pdf.")
                    continue
                new_path = os.path.join(SCRIPT_DIR, new_name)
                if os.path.exists(new_path):
                    print(f"  [WARN] '{new_name}' also already exists. Choose again.")
                    continue
                return new_path
        elif choice == "3":
            print("Aborted.")
            sys.exit(0)
        else:
            print("  [ERROR] Please enter 1, 2, or 3.")


def collect_files():
    if not os.path.isdir(INPUT_DIR):
        print(f"[ERROR] Input folder does not exist: {INPUT_DIR}")
        sys.exit(1)

    all_entries = [
        f for f in os.listdir(INPUT_DIR)
        if os.path.isfile(os.path.join(INPUT_DIR, f)) and not f.startswith(".")
    ]

    if not all_entries:
        print("[ERROR] No files found in ./to-combine/. Nothing to combine.")
        sys.exit(1)

    unsupported = {
        f for f in all_entries
        if os.path.splitext(f)[1].lower() not in SUPPORTED_EXTS
    }
    for f in unsupported:
        ext = os.path.splitext(f)[1] or "(no extension)"
        print(f"[WARN] Unsupported file type '{ext}' for '{f}'. Skipping.")

    supported = sorted(
        [f for f in all_entries if f not in unsupported],
        key=lambda x: x.lower(),
    )
    return supported


def image_to_temp_pdf(filepath):
    with Image.open(filepath) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Close before saving — img.save requires the file to be closed on Windows
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        try:
            img.save(tmp.name, "PDF", resolution=150)
        except Exception:
            os.unlink(tmp.name)
            raise
    return tmp.name


def merge_and_write(pdf_paths, output_path):
    writer = PdfWriter()
    for path in pdf_paths:
        writer.append(path)
    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()


def main():
    args = parse_args()
    output_path = resolve_output_path(args.output)

    if os.path.exists(output_path):
        output_path = prompt_output_collision(output_path)

    files = collect_files()

    temp_files = []
    pdf_paths = []

    print(f"\nProcessing {len(files)} file(s) from ./to-combine/...\n")

    for filename in files:
        filepath = os.path.join(INPUT_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()
        try:
            if ext in PDF_EXTS:
                pdf_paths.append(filepath)
                print(f"  [OK] {filename}")
            elif ext in IMAGE_EXTS:
                temp_path = image_to_temp_pdf(filepath)
                temp_files.append(temp_path)
                pdf_paths.append(temp_path)
                print(f"  [OK] {filename} (converted from image)")
        except Exception as e:
            print(f"  [WARN] Could not process '{filename}': {e}. Skipping.")

    if not pdf_paths:
        print("\n[ERROR] No files could be processed. Output PDF not created.")
        sys.exit(1)
    try:
        merge_and_write(pdf_paths, output_path)
        output_name = os.path.basename(output_path)
        print(f"\nDone. {len(pdf_paths)} file(s) combined into '{output_name}'.")
    except Exception as e:
        print(f"\n[ERROR] Failed to write output PDF: {e}")
        sys.exit(1)
    finally:
        for tmp in temp_files:
            try:
                os.unlink(tmp)
            except OSError:
                pass


if __name__ == "__main__":
    main()

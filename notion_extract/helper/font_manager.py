import os
import shutil
import tempfile
import requests
import tarfile
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def ensure_font_available(font_name="DejaVuSans", font_url=None):
    """Ensures that the required font is available for use."""
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    font_files = {
        "DejaVuSans": {
            "regular": {
                "path": os.path.join(fonts_dir, "DejaVuSans.ttf"),
                "url": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2"
            },
            "bold": {
                "path": os.path.join(fonts_dir, "DejaVuSans-Bold.ttf"),
                "url": "https://downloads.sourceforge.net/project/dejavu/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2"
            }
        }
    }
    
    # Download and save fonts if they don't exist
    # Check if any font in the font family needs to be downloaded
    need_download = False
    for style, font_info in font_files.get(font_name, {}).items():
        if not os.path.exists(font_info["path"]):
            need_download = True
            break
    
    # Download and extract the archive only once if any font is missing
    if need_download:
        try:
            # Get URL from the first font (they're all the same archive)
            url = next(iter(font_files.get(font_name, {}).values()))["url"]
            print(f"Downloading {font_name} fonts archive...")
            
            # Download the archive to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".tar.bz2", delete=False) as temp_file:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, temp_file)
                archive_path = temp_file.name
            
            # Extract the required font files
            with tarfile.open(archive_path, "r:bz2") as tar:
                for style, font_info in font_files.get(font_name, {}).items():
                    font_filename = os.path.basename(font_info["path"])
                    # Find the TTF file in the archive
                    for member in tar.getmembers():
                        if member.name.endswith(font_filename):
                            # Extract the font file
                            f = tar.extractfile(member)
                            with open(font_info["path"], 'wb') as font_file:
                                shutil.copyfileobj(f, font_file)
                            print(f"Extracted {font_name} {style} font to {font_info['path']}")
                            break
            
            # Clean up
            os.unlink(archive_path)
        except Exception as e:
            print(f"Error downloading or extracting fonts: {e}")
            return False
    
    # Now check that all fonts exist after download attempt
    for style, font_info in font_files.get(font_name, {}).items():
        font_path = font_info["path"]
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return False
        # print(f"Using {font_name} {style} font: {font_path}")
    
    # Register fonts with reportlab
    try:
        if "DejaVuSans" not in pdfmetrics._fonts:
            # Register both original case and lowercase versions for regular font
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_files["DejaVuSans"]["regular"]["path"]))
            pdfmetrics.registerFont(TTFont('dejavusans', font_files["DejaVuSans"]["regular"]["path"]))
            
            # Register both original case and lowercase versions for bold font
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_files["DejaVuSans"]["bold"]["path"]))
            pdfmetrics.registerFont(TTFont('dejavusans-bold', font_files["DejaVuSans"]["bold"]["path"]))
        return True
    except Exception as e:
        print(f"Error registering fonts: {e}")
        return False
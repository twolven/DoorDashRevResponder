# DoorDash Review Responder

An automated tool for responding to DoorDash restaurant reviews. Uses image recognition to detect review ratings and provide appropriate responses with optional discount offers for customer retention.

## Features

- Automated review detection and response
- Star rating detection (1-5 stars)
- Customizable response templates
- Discount tracking system
- Human-like typing simulation
- Random intervals between actions to prevent detection
- Basic OCR for customer name detection

## Requirements

- Python 3.8+
- PyAutoGUI
- OpenCV (cv2)
- Pytesseract
- numpy

## Recommended Setup

For optimal performance and reliability, it's recommended to run this tool in a virtual machine:

1. Set up a VM with a lightweight Linux distribution (e.g., Lubuntu or Xubuntu)
   - Recommended VM specs: 2GB RAM, 2 CPU cores, 20GB storage
   - Enable desktop environment and display settings
   - Configure display resolution to match your source images

2. Inside the VM, install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

3. Ensure all required images are in the project directory:
- Star rating images (1-5 stars)
- Button images
- Text box images

## Usage

Important: It's recommended to run this tool in a dedicated virtual machine to ensure consistent screen resolution and prevent interference with your regular computer usage.

1. Log into your DoorDash merchant account
2. Navigate to the reviews section
3. Run the script:
```bash
python ddrev.py
```

The script will:
- Check for new reviews at random intervals (4-6 hours)
- Automatically respond based on rating
- Track discounts offered to customers
- Simulate human-like interaction

## Configuration

The script uses several constants that can be modified:
- `REVIEW_CHECK_INTERVAL`: Time between review checks
- `MAX_RETRIES`: Number of retry attempts for actions
- `DISCOUNT_TRACKER_FILE`: File to store discount history

## Contributing

Feel free to submit issues and enhancement requests!

## Disclaimer

This tool is for educational purposes only. Be sure to comply with DoorDash's terms of service and policies when managing your restaurant's reviews. Running automation tools in a virtual machine helps prevent accidental interactions with other applications and provides a consistent environment for the image recognition features.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

This means:
- You can freely view and use this code
- If you modify or distribute it, you must:
  - Make your source code publicly available
  - License it under AGPL-3.0
  - Document your changes
  - Include the original copyright and license
- Commercial use requires making the complete source code available
import pyautogui
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import pytesseract
from pathlib import Path
import cv2
import numpy as np
import random

# Set up logging with rotation
log_file = "doordash_review.log"
max_bytes = 5 * 1024 * 1024  # 5MB per file
backup_count = 5  # Keep 5 backup files

# Configure the rotating file handler
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=max_bytes,
    backupCount=backup_count,
    encoding='utf-8'
)

# Configure console handler with a more concise format
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message).80s'))

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Clear any existing handlers to avoid duplication
for handler in logger.handlers[:]:
    if isinstance(handler, logging.StreamHandler):
        logger.removeHandler(handler)

# Constants
DISCOUNT_TRACKER_FILE = "discount_tracker.json"
MAX_RETRIES = 3
REVIEW_CHECK_INTERVAL = random.randint(240, 360)  # Random interval between 4-6 minutes
TEMPLATE_POSITIONS = {
    "Your feedback is important to us": 1,
    "We're sorry to hear about your issue": 2,
    "We're confident we'll do better next time": 3,
    "Thank you for your review": 4,
    "We're glad you had a great experience": 5,
    "None": 6
}

def human_pause(min_seconds=0.5, max_seconds=2.0):
    """Random pause to simulate human behavior"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def load_discount_tracker():
    try:
        with open(DISCOUNT_TRACKER_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_discount_tracker(tracker):
    with open(DISCOUNT_TRACKER_FILE, 'w') as f:
        json.dump(tracker, f)

discount_tracker = load_discount_tracker()

def add_random_offset(x, y, max_offset=5):
    """Add a small random offset to click coordinates"""
    return (
        x + random.randint(-max_offset, max_offset),
        y + random.randint(-max_offset, max_offset)
    )

def find_and_click(image_name, confidence=0.8, retries=MAX_RETRIES):
    """Find and click on an image on screen with retries"""
    for attempt in range(retries):
        try:
            location = pyautogui.locateCenterOnScreen(image_name, confidence=confidence)
            if location:
                x, y = add_random_offset(location[0], location[1])
                human_pause(0.2, 0.5)  # Brief pause before click
                # Move to position first
                pyautogui.moveTo(x, y)
                human_pause(0.2, 0.3)  # Small pause after move
                # Perform explicit mousedown and mouseup
                pyautogui.mouseDown()
                human_pause(0.1, 0.2)  # Small pause between down and up
                pyautogui.mouseUp()
                human_pause(0.3, 0.8)  # Brief pause after click
                return True
            if attempt < retries - 1:  # Don't sleep on last attempt
                human_pause(0.5, 1.0)  # Wait before retry
        except Exception as e:
            logging.error(f"Error finding {image_name} (attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                human_pause(1.0, 2.0)  # Longer wait on error
    return False

def refresh_page():
    """Refresh the page using multiple fallback methods"""
    try:
        # First ensure browser window is in focus
        if find_and_click("lifetime.png", confidence=0.9):
            human_pause(0.5, 1.0)  # Brief pause after focusing
            
            # Now try Ctrl+R (Linux/Windows) or Cmd+R (Mac)
            pyautogui.hotkey('ctrl', 'r')
            human_pause(3.0, 5.0)  # Wait for potential refresh
            
            # Second attempt: Try F5 if first attempt didn't work
            if not find_and_click("lifetime.png", confidence=0.9):
                logging.info("First refresh attempt may have failed, trying F5")
                pyautogui.press('f5')
                human_pause(3.0, 5.0)
            
            # Third attempt: Try clicking browser refresh button location
            if not find_and_click("lifetime.png", confidence=0.9):
                logging.info("Second refresh attempt may have failed, trying browser refresh button")
                # Typical browser refresh button location (adjust coordinates as needed)
                pyautogui.click(x=100, y=50)  # Approximate refresh button location
                human_pause(3.0, 5.0)
            
            # Final verification
            for attempt in range(3):
                if find_and_click("lifetime.png", confidence=0.9):
                    logging.info("Page refreshed successfully")
                    return True
                human_pause(1.0, 2.0)
            
            logging.error("All refresh attempts failed")
            return False
        else:
            logging.error("Could not find lifetime.png to focus browser window")
            return False
            
    except Exception as e:
        logging.error(f"Error during page refresh: {e}")
        return False

def get_star_rating():
    """Determine star rating by checking for star patterns"""
    logging.info("Starting star rating detection")
    for stars in range(5, 0, -1):
        for attempt in range(MAX_RETRIES):
            logging.debug(f"Checking for {stars} stars (attempt {attempt + 1})")
            if pyautogui.locateOnScreen(f"{stars}star.png", confidence=0.95):  # Increased from 0.8 to 0.95
                logging.info(f"Detected {stars}-star rating")
                return stars
            human_pause(0.2, 0.5)
    logging.warning("Failed to detect star rating, defaulting to 0")
    return 0

def type_like_human(text):
    """Type text with random delays between keystrokes, balanced for speed and accuracy"""
    # Type in small chunks to seem natural while being faster
    chunk_size = random.randint(2, 4)  # Smaller chunks for better accuracy
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    for chunk in chunks:
        pyautogui.typewrite(chunk)
        human_pause(0.03, 0.07)  # Slightly longer delay between chunks for reliability

def get_customer_name():
    """Get the customer name from the review panel using basic OCR"""
    screenshot = pyautogui.screenshot()
    review_text = pytesseract.image_to_string(screenshot)
    lines = [line.strip() for line in review_text.split('\n') if line.strip()]
    # Usually the customer name is one of the first short lines
    for line in lines[:5]:  # Check first 5 lines
        if len(line) < 30 and not any(word in line.lower() for word in ['star', 'review', 'respond', 'template']):
            return line
    return "Unknown"

def respond_to_review():
    rating = get_star_rating()
    customer_name = get_customer_name() if rating <= 2 else "Customer"
    human_pause(0.5, 1.0)
    
    # Determine response based on rating
    if rating >= 4:
        response = "It was a pleasure serving you. We appreciate you taking the time to share your feedback and being so open with us. We're happy you enjoyed our service, and we hope you'll come and see us again soon!"
        discount = 2
    elif rating == 3:
        # Distinct message for 3-star reviews
        response = "Thanks for your balanced feedback. We're always working to improve our service and your insights help us do that. We appreciate you taking the time to share your experience and hope to serve you again soon!"
        discount = 1  # $1 discount for 3-star reviews
    else:  # 1-2 stars
        response = "We're sorry to hear about your issue. We understand your frustration and will look to improve so we can provide a better experience for your next time"
        if customer_name not in discount_tracker:
            discount = 5
            discount_tracker[customer_name] = True
            save_discount_tracker(discount_tracker)
            logging.info(f"First-time low rating from {customer_name}, giving $5 discount")
        else:
            discount = 0
            logging.info(f"Repeat low rating from {customer_name}, no additional discount")
    
    # Log the rating and response for debugging
    logging.info(f"Processing {rating}-star review with response type and discount: ${discount}")
    
    # Type the response
    if not find_and_click('text_box.png'):
        logging.error("Failed to find text box")
        return False
        
    type_like_human(response)
    human_pause(0.8, 1.5)
    
    # Set discount only if greater than 0
    if discount > 0:
        if not find_and_click("other_discount.png"):
            logging.error("Failed to click other discount")
            return False
        
        human_pause(0.5, 1.0)
        if not find_and_click("amount_box.png"):
            logging.error("Failed to click amount box")
            return False
            
        type_like_human(str(discount))
    
    human_pause(0.8, 1.5)
    
    # Send response
    if not find_and_click("send_button.png"):
        logging.error("Failed to click send button")
        return False
    
    human_pause(1.5, 2.5)
    return True

def check_and_respond():
    logging.info("Checking for new reviews")
    
    # Refresh the page before checking for new reviews
    if not refresh_page():
        logging.error("Failed to refresh page, continuing with existing page state")
    
    reviews_processed = 0
    while find_and_click("respond_button.png"):
        human_pause(1.0, 2.0)  # Wait for response panel
        if not respond_to_review():
            logging.warning("Failed to process review, moving to next one")
            human_pause(2.0, 3.0)
            continue
        
        reviews_processed += 1
        human_pause(1.5, 3.0)  # Variable wait between reviews
    
    if reviews_processed > 0:
        logging.info(f"Processed {reviews_processed} reviews")
    else:
        logging.info("No new reviews found")

def main():
    logging.info("Starting DoorDash review responder")
    
    while True:
        # Immediate check on startup
        check_and_respond()
        
        # Wait for next interval
        wait_time = random.randint(14400, 21600)  # 4-6 hours in seconds
        hours = wait_time // 3600
        minutes = (wait_time % 3600) // 60
        logging.info(f"Waiting approximately {hours} hours and {minutes} minutes before next check")
        human_pause(wait_time, wait_time + 300)  # Add up to 5 minutes of randomness
        
        # Check again after waiting
        check_and_respond()

if __name__ == "__main__":
    main()
from flask import Blueprint, request, jsonify, current_app
import os
import logging
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
import pytesseract
from api.utils import get_current_user_id

# Try to import OpenCV and NumPy
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

ocr_api = Blueprint('ocr_api', __name__)
logger = logging.getLogger(__name__)

def setup_ocr():
    """Setup OCR configuration"""
    try:
        # Try to set Tesseract path for Windows
        if os.name == 'nt':  # Windows
            # Common Tesseract installation paths on Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    break
            else:
                logger.warning("Tesseract not found in common Windows paths. Please install Tesseract OCR.")
        else:
            # Linux/Mac - assume tesseract is in PATH
            logger.info("Using system Tesseract installation")
            
    except Exception as e:
        logger.error(f"Error setting up OCR: {e}")

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    try:
        if not OPENCV_AVAILABLE:
            # Fallback: return image as-is if OpenCV is not available
            logger.warning("OpenCV not available, skipping image preprocessing")
            return image
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return image

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        if not OPENCV_AVAILABLE:
            # Fallback: use PIL for image reading if OpenCV is not available
            try:
                from PIL import Image
                image = Image.open(image_path)
                processed_image = image
                logger.info("Using PIL for image processing (OpenCV not available)")
            except ImportError:
                logger.error("Neither OpenCV nor PIL available for image processing")
                return {"text": "", "confidence": 0, "error": "No image processing library available"}
        else:
            # Read image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image file")
            
            # Preprocess image
            processed_image = preprocess_image(image)
        
        # Extract text using Tesseract
        # Try different OCR configurations for better results
        configs = [
            '--oem 3 --psm 6',  # Default configuration
            '--oem 3 --psm 3',  # Fully automatic page segmentation
            '--oem 3 --psm 8',  # Single word
            '--oem 3 --psm 13'  # Raw line
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in configs:
            try:
                # Extract text with confidence
                data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    # Extract text
                    text = ' '.join([word for word, conf in zip(data['text'], data['conf']) if int(conf) > 30])
                    
                    if avg_confidence > best_confidence and text.strip():
                        best_confidence = avg_confidence
                        best_text = text
                        
            except Exception as e:
                logger.warning(f"OCR config {config} failed: {e}")
                continue
        
        # If no good results, try simple text extraction
        if not best_text.strip():
            best_text = pytesseract.image_to_string(processed_image)
        
        return {
            'text': best_text.strip(),
            'confidence': best_confidence,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return {
            'text': '',
            'confidence': 0,
            'success': False,
            'error': str(e)
        }

@ocr_api.route('/api/ocr/extract', methods=['POST'])
def ocr_extract_text():
    """Extract text from uploaded image using OCR"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = upload_dir / unique_filename
        
        file.save(str(file_path))
        
        # Extract text using OCR
        result = extract_text_from_image(str(file_path))
        
        # Clean up uploaded file
        try:
            os.remove(str(file_path))
        except:
            pass  # Ignore cleanup errors
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'confidence': result['confidence'],
                'message': 'Text extracted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to extract text from image')
            }), 500
            
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ocr_api.route('/api/ocr/extract-batch', methods=['POST'])
def ocr_extract_batch():
    """Extract text from multiple uploaded images"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'No image files uploaded'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        
        # Validate file types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        results = []
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        for file in files:
            if file.filename == '':
                continue
                
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file type'
                })
                continue
            
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = upload_dir / unique_filename
                
                file.save(str(file_path))
                
                # Extract text using OCR
                result = extract_text_from_image(str(file_path))
                
                # Clean up uploaded file
                try:
                    os.remove(str(file_path))
                except:
                    pass
                
                results.append({
                    'filename': file.filename,
                    'success': result['success'],
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0),
                    'error': result.get('error', '')
                })
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Processed {len(results)} images'
        })
        
    except Exception as e:
        logger.error(f"Batch OCR extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
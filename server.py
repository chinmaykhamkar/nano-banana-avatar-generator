#!/usr/bin/env python3
"""
Notion Avatar Generator - Python Server
Converts photos to Notion-style avatars using Google GenAI
"""

import os
import io
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import google.genai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = Path('public/outputs')
REFERENCE_FOLDER = Path('public')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Ensure directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize GenAI client
client = None
reference_images = []

def init_genai():
    """Initialize Google GenAI client"""
    global client
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        logger.info("Google GenAI client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        return False

def load_reference_images():
    """Load reference images for style consistency"""
    global reference_images
    reference_images = []
    
    ref_paths = [
        REFERENCE_FOLDER / 'reference-avatar-2.png',
        REFERENCE_FOLDER / 'reference-avatar-3.png',
        REFERENCE_FOLDER / 'reference-image-6.png'
    ]
    
    for ref_path in ref_paths:
        try:
            if ref_path.exists():
                with Image.open(ref_path) as img:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    reference_images.append(img.copy())
                logger.info(f"Loaded reference image: {ref_path.name}")
            else:
                logger.warning(f"Reference image not found: {ref_path}")
        except Exception as e:
            logger.error(f"Error loading reference image {ref_path}: {e}")
    
    logger.info(f"Loaded {len(reference_images)} reference images")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_notion_style(user_image: Image.Image) -> Optional[Image.Image]:
    """Convert user image to Notion style using GenAI with reference images"""
    if not client:
        raise Exception("GenAI client not initialized")
    
    try:
        # Prepare the prompt
        prompt = """STYLE REFERENCE EXAMPLES: The first 3 images show the EXACT Notion avatar style to replicate.

TASK: Convert the final photo into the same minimalist black and white avatar style as the reference examples.

CRITICAL: FACE AND HEAD ONLY
• Show ONLY the person's face and head - nothing below the neck
• Even if the source photo shows shoulders, chest, or body - ignore these parts
• Focus exclusively on facial features, hair, and head shape
• Create a head-and-shoulders composition but only draw the head part

STYLE REQUIREMENTS (match references exactly):
• Pure black lines on white background
• Clean, simple geometric shapes
• Minimalist cartoon illustration
• Square format (1:1 aspect ratio)
• Thick, bold black line weight (not thin lines)
• Strong contrast and bold styling

ANALYZE THE PERSON CAREFULLY:
• Look ONLY at what is actually visible in the photo
• Hair style, glasses, face shape, actual facial hair presence
• Do NOT assume or add features that aren't clearly visible

CONVERT FOLLOWING THESE RULES:

FACE:
• Simple oval/circle matching their actual face shape
• EYES: Be creative but accurate - use ovals, circles, or simple shapes that match their eye shape and expression. Can show eyelashes, eye direction, or subtle expressions if visible in source
• EYEBROWS: Match their actual eyebrow shape and thickness - can be straight lines, arches, or thick shapes depending on the person's real eyebrows
• Minimal nose indication (small line or dot)  
• Simple curved line for mouth that reflects their expression
• Stay true to their actual facial structure and expressions

HAIR:
• Bold, solid black shapes with thick outlines
• Match their actual hair volume and style
• For curly hair: simple wavy shapes, not overly dense
• For straight hair: clean geometric shapes
• Keep hair proportionate and realistic to source
• Use thick black lines consistent with Notion style

FACIAL HAIR - CRITICAL RULE:
• ONLY add facial hair if it's CLEARLY visible in the source photo
• If the person appears clean-shaven, DO NOT add any beard or mustache
• If uncertain about facial hair presence, leave the face clean
• When facial hair IS present: use light, minimal black shapes

GENDER REPRESENTATION:
• Focus on accuracy over gender stereotypes
• Use subtle differences in face shape and features
• Don't over-emphasize masculine/feminine traits
• Eye and eyebrow styles should match the individual, not gender assumptions

ACCESSORIES:
• Glasses: Simple geometric frame shapes
• Keep essential identifying accessories

COMPOSITION:
• HEAD AND FACE ONLY - no clothing, no body parts
• If you must show a tiny bit of neck/collar area, keep it minimal
• Focus 95% on the face and hair

FINAL INSTRUCTION:
Create a clean, conservative Notion-style avatar that:
• Accurately represents ONLY what's visible in the source photo
• Uses subtle, proportionate styling - not heavy or exaggerated
• Preserves the person's actual identity without adding fictional elements
• Matches the reference style while staying true to the source image

REMEMBER: When in doubt, be conservative and accurate rather than stylized."""

        # Prepare content list: reference images + user image + prompt
        contents = []
        
        # Add reference images first
        for ref_img in reference_images:
            contents.append(ref_img)
        
        # Add user image
        contents.append(user_image)
        
        # Add text prompt
        contents.append(prompt)
        
        logger.info(f"Generating content with {len(contents)} items ({len(reference_images)} references + 1 user image + 1 prompt)")
        
        # Generate content
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=contents
        )
        
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        # Extract generated images using the approach from your working Python example
        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if hasattr(part, 'inline_data') and part.inline_data
        ]
        
        logger.info(f"Found {len(image_parts)} image parts")
        
        if image_parts:
            try:
                # Use the first image part (like in your reference code)
                image_data = image_parts[0]
                logger.info(f"Image data type: {type(image_data)}")
                logger.info(f"Image data length: {len(image_data) if hasattr(image_data, '__len__') else 'No length'}")
                
                # Create image from bytes (following your reference pattern)
                if isinstance(image_data, bytes):
                    # Direct bytes
                    generated_image = Image.open(io.BytesIO(image_data))
                elif isinstance(image_data, str):
                    # Base64 encoded string - decode it
                    decoded_data = base64.b64decode(image_data)
                    generated_image = Image.open(io.BytesIO(decoded_data))
                else:
                    logger.error(f"Unexpected image data type: {type(image_data)}")
                    return None
                
                logger.info("Successfully generated Notion-style avatar")
                return generated_image
                
            except Exception as e:
                logger.error(f"Error processing image data: {e}")
                if image_parts:
                    logger.error(f"First 50 chars of image data: {str(image_parts[0])[:50]}")
                return None
        else:
            # Log text responses for debugging
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    logger.info(f"AI Response Text: {part.text[:200]}...")
                else:
                    logger.info(f"Part type: {type(part)}, attributes: {[attr for attr in dir(part) if not attr.startswith('_')]}")
            
            logger.error("No image parts found in response")
            return None
        
    except Exception as e:
        logger.error(f"Error in convert_to_notion_style: {e}")
        raise

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('public', 'index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'genai_initialized': client is not None,
        'reference_images_loaded': len(reference_images),
        'api_key_configured': bool(os.getenv('GEMINI_API_KEY'))
    })

@app.route('/convert', methods=['POST'])
def convert_image():
    """Convert uploaded image to Notion style"""
    try:
        # Check if client is initialized
        if not client:
            return jsonify({'error': 'GenAI client not initialized'}), 500
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, BMP, or WebP'}), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Seek back to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
        
        logger.info(f"Processing image: {file.filename}, size: {file_size} bytes")
        
        # Load and process the image
        try:
            user_image = Image.open(file.stream)
            
            # Convert to RGB if necessary
            if user_image.mode != 'RGB':
                user_image = user_image.convert('RGB')
            
            # Generate Notion-style avatar
            generated_image = convert_to_notion_style(user_image)
            
            if generated_image is None:
                return jsonify({'error': 'Failed to generate avatar'}), 500
            
            # Save the generated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"notion_avatar_{timestamp}.png"
            filepath = UPLOAD_FOLDER / filename
            
            generated_image.save(filepath, 'PNG')
            logger.info(f"Saved generated image: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'Image converted successfully',
                'results': [{
                    'fileName': filename,
                    'filePath': f'/outputs/{filename}',
                    'mimeType': 'image/png'
                }]
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in convert_image: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve generated images"""
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Initialize GenAI
    if not init_genai():
        logger.error("Failed to initialize GenAI client. Please check your GEMINI_API_KEY.")
        exit(1)
    
    # Load reference images
    load_reference_images()
    
    # Get port from environment or use default
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
    logger.info(f"Reference images loaded: {len(reference_images)}")
    
    app.run(host='0.0.0.0', port=port, debug=True)

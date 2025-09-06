# Notion Avatar Generator

Transform your photos into clean, minimalist Notion-style avatars using Google's GenAI API.

## Demo


https://github.com/user-attachments/assets/78b6b2db-79ab-43c7-8d59-0577cebf7d38




## Features

- 🎨 Convert photos to Notion-style black and white avatars
- 🖥️ Modern, responsive web interface
- 📱 Drag and drop or click to upload
- 💾 Download generated avatars
- ⚡ Fast processing with Google GenAI
- 🎯 Reference image guidance for consistent results

## Setup

### 1. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set up Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Google GenAI API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_PORT=5000
   ```

### 3. Get Google GenAI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 4. Run the Application

```bash
python server.py
```

The app will be available at `http://localhost:5000`

## How It Works

1. **Reference Images**: The system uses your provided Notion-style examples as reference
2. **Upload**: Users can drag and drop or click to upload their photo
3. **Convert**: The app sends the image + references to Google's GenAI API with a specialized prompt
4. **Download**: Users can download the generated Notion-style avatar

## API Prompt Strategy

The application uses a carefully crafted prompt along with reference images to ensure consistent Notion-style output:

- **Reference Guidance**: Shows the AI your example images first
- **Style Requirements**: Black and white line art, clean geometry
- **Facial Features**: Simplified eyes, nose, mouth with specific guidelines
- **Hair Styling**: Solid black shapes instead of individual strands
- **Accessories**: Simplified glasses/features while maintaining identity
- **Output Format**: Square aspect ratio (1:1), high contrast

## File Structure

```
├── server.py              # Flask server with GenAI integration
├── requirements.txt       # Python dependencies
├── public/
│   ├── index.html         # Frontend interface
│   ├── reference-avatar-1.png  # Reference Notion avatar 1
│   ├── reference-avatar-2.png  # Reference Notion avatar 2
│   └── outputs/           # Generated avatars storage
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Tech Stack

- **Backend**: Python, Flask
- **AI**: Google GenAI (Gemini 2.5 Flash Image Preview)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Image Processing**: PIL (Pillow)
- **Reference Images**: Your provided Notion-style examples

## API Endpoints

- `GET /` - Main application interface
- `POST /convert` - Convert uploaded image to Notion style
- `GET /health` - Health check and system status
- `GET /outputs/<filename>` - Serve generated images

## Troubleshooting

### Common Issues

1. **"GenAI client not initialized"**
   - Make sure you've created a `.env` file with your API key
   - Check that your API key is valid

2. **"Invalid file type"**
   - Ensure you're uploading PNG, JPG, JPEG, GIF, BMP, or WebP files

3. **"File too large"**
   - Compress your image or use a file smaller than 10MB

4. **"No image generated"**
   - Check your internet connection
   - Verify your API key has sufficient quota
   - Try with a different image

### Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development
python server.py
```

## Reference Images

The system uses two reference images (`reference-avatar-1.png` and `reference-avatar-2.png`) to guide the AI in generating consistent Notion-style avatars. These are your original examples that show the desired output style.

## License

MIT License - feel free to use this project for personal or commercial purposes.

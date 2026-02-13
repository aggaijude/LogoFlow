from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
from huggingface_hub import InferenceClient
import os
import io
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-names', methods=['POST'])
def generate_names():
    data = request.json
    description = data.get('description')
    model_name = data.get('model', 'gemini-3-flash-preview')
    
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        return jsonify({'error': 'Server Configuration Error: GOOGLE_API_KEY not set'}), 500

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Act as a world-class branding agency. 
        Project: {description}
        Task: Create 3 unique, modern, and memorable brand names.
        Output: ONLY the 3 names separated by commas. No numbering.
        """
        response = model.generate_content(prompt)
        names = [n.strip() for n in response.text.split(',')][:3]
        return jsonify({'names': names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-logo', methods=['POST'])
def generate_logo():
    data = request.json
    brand_name = data.get('name')
    description = data.get('description')
    model_id = data.get('model', 'black-forest-labs/FLUX.1-schnell')
    
    api_key = os.environ.get("HF_API_TOKEN")

    if not api_key:
        return jsonify({'error': 'Server Configuration Error: HF_API_TOKEN not set'}), 500

    try:
        client = InferenceClient(token=api_key)
        prompt = f"""
        Logo for "{brand_name}". {description}.
        Style: Minimalist, vector, flat, gradient, modern, tech, white background.
        High quality, 4k.
        """
        image = client.text_to_image(prompt, model=model_id)
        
        # Convert image to base64 for frontend
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({'image': f"data:image/png;base64,{img_str}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

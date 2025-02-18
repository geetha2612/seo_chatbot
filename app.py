from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from playwright.sync_api import sync_playwright

# Initialize Flask app
app = Flask(__name__)
run_with_ngrok(app)  # Start ngrok when the app is run

# Set your Hugging Face token directly in the code (for testing only)
hf_token = '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'  # Replace with your actual token

# Log in to Hugging Face
login(token=hf_token)  # Log in to Hugging Face

# Load the tokenizer and model directly
tokenizer = AutoTokenizer.from_pretrained("openai-community/gpt2", use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained("openai-community/gpt2", use_auth_token=hf_token)

def scrape_seo_data(url):
    """Scrape SEO data from the given URL."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        title = page.title()
        meta_description = page.query_selector("meta[name='description']").get_attribute("content") if page.query_selector("meta[name='description']") else "No meta description"
        meta_keywords = page.query_selector("meta[name='keywords']").get_attribute("content") if page.query_selector("meta[name='keywords']") else "No meta keywords"
        links = [a.get_attribute("href") for a in page.query_selector_all("a")]

        browser.close()
        
        return {
            "title": title,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "links": links
        }

@app.route('/seo-query', methods=['POST'])
def seo_query():
    """Handle SEO queries from users."""
    data = request.json
    url = data['url']
    question = data['question']
    
    # Scrape SEO data (assuming this function is defined)
    seo_data = scrape_seo_data(url)
    
    # Prepare the input text
    input_text = f"Question: {question}\nSEO Data: {seo_data}\nAnswer:"
    
    # Tokenize the input and truncate if necessary
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
    
    # Generate a response using the model
    outputs = model.generate(inputs, max_new_tokens=100, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return jsonify({"response": response, "seo_data": seo_data})

if __name__ == '__main__':
    app.run()
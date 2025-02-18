from flask import Flask, request, jsonify
import asyncio
import main  # Ensure this imports your main.py file properly

app = Flask(__name__)

@app.route('/seo', methods=['POST'])
def seo():
    data = request.json
    url = data.get('url')
    question = data.get('question')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    result = loop.run_until_complete(main.seo_chatbot(url, question))  # Call your existing function
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

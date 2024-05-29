from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

conversation = []

@app.route('/input', methods=['POST'])
def handle_input():
    input_text = request.json.get('text')
    if input_text == "quit":
        conversation.clear()
    else:
        conversation.append(("user", input_text))
        # Here you would integrate LangChain to get the response
        response = "Sample response to: " + input_text
        conversation.append(("system", response))
    return jsonify(success=True)

@app.route('/conversation', methods=['GET'])
def get_conversation():
    return jsonify(conversation)

if __name__ == '__main__':
    app.run(port=5000)

import requests

while True:
    input_text = input('Ask a question or type "quit" to exit the conversation: ').strip().lower()
    response = requests.post('http://localhost:5000/input', json={'text': input_text})
    if input_text == "quit":
        break
    if response.status_code != 200:
        print("Failed to send input")

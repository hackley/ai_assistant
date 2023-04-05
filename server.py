from flask import Flask, request, jsonify
from agent import run_agent
from chat_history import ChatMessageHistory

app = Flask(__name__)


@app.route('/api/conversation/<session_id>', methods=['GET'])
def list_message(session_id):
    hist = ChatMessageHistory(session_id=session_id)
    messages = hist.json_messages
    response = {
        'status': 'success',
        'messages': messages
    }
    hist.connection.close()
    return jsonify(response)


@app.route('/api/conversation/<session_id>/messages', methods=['POST'])
def create_message(session_id):
    params = request.get_json()

    if 'message' in params:
        message = params['message']
        reply = run_agent(session_id, message)
        response = {
            'status': 'success',
            'reply': reply
        }
    else:
        response = {
            'status': 'error',
            'error_message': 'Must include a "message" attribute.'
        }

    return jsonify(response)


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

from flask import Flask, request, jsonify
from agent import run_agent

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process_request():
    # Get the JSON data from the request
    params = request.get_json()

    if 'message' in params:
        reply = run_agent(params['message'])
        response = {
            'status': 'success',
            'message': reply
        }
    else:
        response = {
            'status': 'error',
            'message': 'No "message" attribute found in the JSON data.'
        }

    return jsonify(response)


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

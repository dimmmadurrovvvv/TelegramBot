import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

sessions = {}

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    data = request.args if request.method == 'GET' else request.get_json(force=True)
    logging.info(f"Received webhook: {data}")

    event = data.get('event')
    sub1 = data.get('sub1')
    event_id = data.get('event_id')

    if event == 'registration' and sub1:
        sessions[sub1] = {'registered': True, 'event_id': event_id}
        logging.info(f"User {sub1} registered successfully with event_id {event_id}")
        return jsonify({'status': 'success'}), 200

    return jsonify({'status': 'ignored', 'message': 'Event not processed'}), 200

@app.route('/check_registration', methods=['GET'])
def check_registration():
    user_id = request.args.get('user_id')
    logging.info(f"Checking registration status for user_id: {user_id}")
    if user_id in sessions and sessions[user_id].get('registered'):
        return jsonify({'registered': True}), 200
    return jsonify({'registered': False}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Хранение сессий
sessions = {}

@app.route('/postback', methods=['POST'])
def postback():
    event = request.json.get('event')
    user_id = request.json.get('user_id')

    logging.info(f"Received postback: Event: {event}, User ID: {user_id}")
    
    # Обработка данных постбэка
    if event == 'registration':
        sessions[user_id] = {'registered': True}
        logging.info(f"User {user_id} registered successfully.")
        return jsonify({'status': 'success'}), 200
    
    return jsonify({'status': 'ignored', 'message': 'Event not processed'}), 200

@app.route('/check_registration', methods=['GET'])
def check_registration():
    user_id = request.args.get('user_id')
    if user_id in sessions and sessions[user_id].get('registered'):
        return jsonify({'registered': True}), 200
    return jsonify({'registered': False}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





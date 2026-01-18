from flask import Blueprint, send_from_directory, request, jsonify
from chatbot import WeddingChatbot

# Create Blueprint
api_blueprint = Blueprint('api', __name__, static_folder="../frontend", template_folder="../frontend")

# Init Chatbot
chatbot = WeddingChatbot()

@api_blueprint.route('/')
def home():
    return send_from_directory('../frontend', 'landing.html')

@api_blueprint.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@api_blueprint.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    # Use remote addr as fallback session id
    session_id = data.get('session_id', request.remote_addr) 
    
    response_data = chatbot.get_response(user_message, session_id)
    return jsonify(response_data)

@api_blueprint.route('/api/check-availability', methods=['POST'])
def check_availability():
    data = request.json
    date_str = data.get('date')
    
    if not date_str:
        return jsonify({'error': 'No date provided'}), 400

    import tools
    result = tools.check_wedding_hall_availability(date_str)
    return jsonify({'available': result['available'], 'message': result['message']})

@api_blueprint.route('/api/inquiry', methods=['POST'])
def inquiry():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({'error': 'Missing required fields'}), 400

    # For now, just log the inquiry. In a real app, this might send an email or save to DB.
    print(f"\n[INQUIRY RECEIVED]\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}\n")
    
    return jsonify({'status': 'success', 'message': 'Thank you for your inquiry. Our team will contact you shortly.'})

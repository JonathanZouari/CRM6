from flask import Blueprint, request
from backend.routes import success_response, error_response
from backend.services import chat_service

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or not data.get("message"):
            return error_response("message is required")
        answer = chat_service.process_chat(data["message"])
        return success_response({"answer": answer})
    except Exception as e:
        return error_response(str(e), 500)

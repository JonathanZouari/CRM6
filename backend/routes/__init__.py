from flask import jsonify


def success_response(data, status=200):
    return jsonify({"success": True, "data": data}), status


def error_response(message, status=400):
    return jsonify({"success": False, "error": message}), status


def register_blueprints(app):
    from backend.routes.customers import customers_bp
    from backend.routes.orders import orders_bp
    from backend.routes.tasks import tasks_bp
    from backend.routes.chat import chat_bp

    app.register_blueprint(customers_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(chat_bp)

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.db import init_pool
from backend.routes import register_blueprints


def create_app():
    Config.validate()

    app = Flask(__name__)
    CORS(app, origins=Config.ALLOWED_ORIGINS)

    init_pool(Config.DATABASE_URL)
    register_blueprints(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"success": True, "data": {"status": "ok"}})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

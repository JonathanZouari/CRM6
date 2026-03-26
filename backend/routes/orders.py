from flask import Blueprint, request
from routes import success_response, error_response
from services import order_service

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/customers/<customer_id>/orders", methods=["GET"])
def list_orders(customer_id):
    try:
        orders = order_service.get_orders_by_customer(customer_id)
        return success_response(orders)
    except Exception as e:
        return error_response(str(e), 500)


@orders_bp.route("/customers/<customer_id>/orders", methods=["POST"])
def create_order(customer_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required")
        for field in ["destination", "departure_date", "price"]:
            if not data.get(field):
                return error_response(f"{field} is required")
        order = order_service.create_order(customer_id, data)
        return success_response(order, 201)
    except Exception as e:
        return error_response(str(e), 500)


@orders_bp.route("/orders/<order_id>", methods=["PUT"])
def update_order(order_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required")
        order = order_service.update_order(order_id, data)
        if not order:
            return error_response("Order not found", 404)
        return success_response(order)
    except Exception as e:
        return error_response(str(e), 500)


@orders_bp.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    try:
        deleted = order_service.delete_order(order_id)
        if not deleted:
            return error_response("Order not found", 404)
        return success_response({"deleted": True})
    except Exception as e:
        return error_response(str(e), 500)

from flask import Blueprint, request
from routes import success_response, error_response
from services import customer_service

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/customers", methods=["GET"])
def list_customers():
    try:
        status_filter = request.args.get("status")
        customers = customer_service.get_all_customers(status_filter)
        return success_response(customers)
    except Exception as e:
        return error_response(str(e), 500)


@customers_bp.route("/customers/late", methods=["GET"])
def list_late_customers():
    try:
        customers = customer_service.get_late_customers()
        return success_response(customers)
    except Exception as e:
        return error_response(str(e), 500)


@customers_bp.route("/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    try:
        customer = customer_service.get_customer_by_id(customer_id)
        if not customer:
            return error_response("Customer not found", 404)
        return success_response(customer)
    except Exception as e:
        return error_response(str(e), 500)


@customers_bp.route("/customers", methods=["POST"])
def create_customer():
    try:
        data = request.get_json()
        if not data or not data.get("name"):
            return error_response("Name is required")
        customer = customer_service.create_customer(data)
        return success_response(customer, 201)
    except Exception as e:
        return error_response(str(e), 500)


@customers_bp.route("/customers/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required")
        customer = customer_service.update_customer(customer_id, data)
        if not customer:
            return error_response("Customer not found", 404)
        return success_response(customer)
    except Exception as e:
        return error_response(str(e), 500)


@customers_bp.route("/customers/<customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    try:
        deleted = customer_service.delete_customer(customer_id)
        if not deleted:
            return error_response("Customer not found", 404)
        return success_response({"deleted": True})
    except Exception as e:
        return error_response(str(e), 500)

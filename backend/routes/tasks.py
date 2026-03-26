from flask import Blueprint, request
from backend.routes import success_response, error_response
from backend.services import task_service

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/customers/<customer_id>/tasks", methods=["GET"])
def list_tasks(customer_id):
    try:
        tasks = task_service.get_tasks_by_customer(customer_id)
        return success_response(tasks)
    except Exception as e:
        return error_response(str(e), 500)


@tasks_bp.route("/customers/<customer_id>/tasks", methods=["POST"])
def create_task(customer_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required")
        for field in ["title", "due_date"]:
            if not data.get(field):
                return error_response(f"{field} is required")
        task = task_service.create_task(customer_id, data)
        return success_response(task, 201)
    except Exception as e:
        return error_response(str(e), 500)


@tasks_bp.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body is required")
        task = task_service.update_task(task_id, data)
        if not task:
            return error_response("Task not found", 404)
        return success_response(task)
    except Exception as e:
        return error_response(str(e), 500)


@tasks_bp.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        deleted = task_service.delete_task(task_id)
        if not deleted:
            return error_response("Task not found", 404)
        return success_response({"deleted": True})
    except Exception as e:
        return error_response(str(e), 500)

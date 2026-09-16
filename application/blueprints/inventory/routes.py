from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from application.models import Inventory, db
from . import inventory_bp

#Create inventory item
@inventory_bp.route("/", methods=["POST"])
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_inventory = Inventory(**inventory_data)

    db.session.add(new_inventory)
    db.session.commit()

    return inventory_schema.jsonify(new_inventory), 201

#Get all inventory
@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    query = select(Inventory)

    inventory = db.session.execute(query).scalars().all()

    return inventories_schema.jsonify(inventory), 200

#Get inventory item by ID
@inventory_bp.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({
            "error": "Inventory item not found."
        }), 404

    return inventory_schema.jsonify(inventory), 200

#Update inventory item
@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({
            "error": "Inventory item not found."
        }), 404

    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in inventory_data.items():
        setattr(inventory, key, value)

    db.session.commit()

    return inventory_schema.jsonify(inventory), 200

#Delete inventory item
@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({
            "error": "Inventory item not found."
        }), 404

    db.session.delete(inventory)
    db.session.commit()

    return jsonify({
        "message": f"Inventory id: {inventory_id}, successfully deleted!"
    }), 200
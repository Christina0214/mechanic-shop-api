from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import ServiceTicket, db, Mechanic, Inventory
from . import service_tickets_bp
from application.utils.util import token_required

#Create a new service ticket
@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201

#Adding a relationship between a service ticket and the mechanic
@service_tickets_bp.route('/<int:ticket_id>/assign_mechanic/<int:mechanic_id>', methods=['PUT'])
def add_ticket(ticket_id, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not mechanic:
        return jsonify({"message": "Invalid mechanic id."}), 404
    
    if not ticket:
        return jsonify({"message": "Invalid service ticket id."}), 404
    
    #Prevent duplicates
    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic is already assigned!"}), 400
    
    ticket.mechanics.append(mechanic)
    db.session.commit()
    
    return jsonify({"message": f"Mechanic {mechanic.name} assigned to service ticket {ticket.id}!"}), 200

#Removes the relationship from the service ticket and the mechanic
@service_tickets_bp.route('/<int:ticket_id>/remove_mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not mechanic:
        return jsonify({"message": "Invalid mechanic id."}), 400
    
    if not ticket:
        return jsonify({"message": "Invalid service ticket id."}), 400
    
    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned."}), 400
    
    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify({"message": f"Successfully removed mechanic {mechanic.name} from service ticket {ticket.id}"}), 200

#Retrieves all service tickets
@service_tickets_bp.route('/', methods=['GET'])
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(tickets), 200

#Retrieve the logged-in customer's service tickets
@service_tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(
        ServiceTicket.customer_id == int(customer_id)
    )

    tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(tickets), 200

@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"message": "Invalid service ticket id."}), 404

    try:
        data = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for mechanic_id in data["remove_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    for mechanic_id in data["add_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()

    return jsonify({"message": "Service ticket updated successfully."}), 200

#To add a single part to an existing Service Ticket
@service_tickets_bp.route("/<int:ticket_id>/add_inventory/<int:inventory_id>", methods=["PUT"])
def add_inventory(ticket_id, inventory_id):

    ticket = db.session.get(ServiceTicket, ticket_id)
    inventory = db.session.get(Inventory, inventory_id)

    if not ticket:
        return jsonify({
            "message": "Invalid service ticket id."
        }), 404

    if not inventory:
        return jsonify({
            "message": "Invalid inventory id."
        }), 404

    if inventory in ticket.inventory:
        return jsonify({
            "message": "Inventory item is already assigned to this ticket."
        }), 400

    ticket.inventory.append(inventory)

    db.session.commit()

    return jsonify({
        "message": f"Inventory item {inventory.name} added to service ticket {ticket.id}!"
    }), 200
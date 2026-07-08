from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import ServiceTicket, db, Mechanic
from . import service_tickets_bp

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
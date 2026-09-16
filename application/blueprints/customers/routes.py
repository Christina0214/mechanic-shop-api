from .schemas import customer_schema, customers_schema, login_schema
from application.blueprints.service_tickets.schemas import service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customer, ServiceTicket, db
from . import customers_bp
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first() #Query user table for a user with this email

    if customer and customer.password == password: #If we have a user associated with the username, validate the password
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "token": token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

#Retrieves all service tickets belonging to the customer who is currently logged in
@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):

    query = select(ServiceTicket).where(
        ServiceTicket.customer_id == customer_id #Makes sure you're only retrieving tickets belonging to the logged-in customer
    )

    tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(tickets), 200

#Create Customer
@customers_bp.route("/", methods=['POST'])
@limiter.limit("3 per hour")  #A client can only attempt to make 3 customers per hour
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#Retrieve Customers
@customers_bp.route("/", methods=['GET'])
@limiter.limit("60 per minute") #Prevents excessive database reads
@cache.cached(timeout=60) #This avoids repeatedly querying the database for the full customer list within the cache timeout
def get_customers():
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = select(Customer)

    customers = db.paginate(
        query,
        page=page,
        per_page=per_page
    )

    return customers_schema.jsonify(customers), 200

#Get a customer by ID
@customers_bp.route("/<int:customer_id>", methods=['GET'])
@limiter.limit("120 per minute") #Reading a single customer is inexpensive, so a higher limit is reasonable
@cache.cached(timeout=60) #If many clients request the same customer, Flask can return the cached response instead of hitting the database each time
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

#Update a customer by ID
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
@token_required
@limiter.limit("20 per hour") #Prevents repeated updates or abuse
def update_customer(token_customer_id, customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if int(token_customer_id) != customer_id:
        return jsonify({
            "error": "You are not authorized to update this customer."
        }), 403
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)
        
    db.session.commit()
    
    return customer_schema.jsonify(customer), 200

#Delete a customer by ID
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
@limiter.limit("10 per hour") #Destructive operation, so stricter limits make sense
@token_required
def delete_customer(token_customer_id, customer_id):
    
    if int(token_customer_id) != customer_id:
        return jsonify({
            "error": "You are not authorized to delete this customer."
        }), 403
        
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted!'}), 200
## Mechanic Shop API

- A Flask REST API for managing a mechanic shop. This application allows users to manage customers, mechanics, and service tickets. Users can create service tickets for customers and assign mechanics to service tickets through a many-to-many relationship.

## Technologies Used
- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Marshmallow
- Flask-Limiter
- Flask-Caching
- Python-JOSE
- SQLite
- Postman

## Features

### Customers
- Create a customer
- Retrieve all customers
- Retrieve a customer by ID
- Update a customer
- Delete a customer
- Customer login
- JWT authentication
- Retrieve service tickets belonging to the logged-in customer
- Pagination for customer results

### Mechanics
- Create a mechanic
- Retrieve all mechanics
- Retrieve a mechanic by ID
- Update a mechanic
- Delete a mechanic
- Retrieve mechanics ranked by the number of service tickets they have worked on

### Service Tickets
- Create a service ticket
- Retrieve all service tickets
- Assign a mechanic to a service ticket
- Remove a mechanic from a service ticket
- Add and remove multiple mechanics from a ticket
- Add inventory parts to a service ticket
- Retrieve service tickets belonging to the logged-in customer

### Inventory
- Create an inventory item
- Retrieve all inventory items
- Retrieve an inventory item by ID
- Update an inventory item
- Delete an inventory item
- Associate inventory parts with service tickets

## Testing

- API endpoints were tested using Postman. A Postman collection is included with the project containing requests for all CRUD operations and service ticket mechanic assignments.

### Authentication & Security

JWT authentication is used for protected customer routes.

When a customer logs in successfully, the API generates a token containing the customer's ID.

Protected requests use:

```text
Authorization: Bearer <token>
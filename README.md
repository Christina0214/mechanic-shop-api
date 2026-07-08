## Mechanic Shop API

- A Flask REST API for managing a mechanic shop. This application allows users to manage customers, mechanics, and service tickets. Users can create service tickets for customers and assign mechanics to service tickets through a many-to-many relationship.

## Technologies Used
- Python
- Flask
- SQLAlchemy
- Marshmallow
- SQLite
- Postman

## Features

### Customers
- Create, view, update, and delete customers.
- Customers can have multiple service tickets.

### Mechanics
- Create, view, update, and delete mechanics.
- Mechanics can be assigned to multiple service tickets.

### Service Tickets
- Create and view service tickets.
- Assign mechanics to service tickets.
- Remove mechanics from service tickets.

## Testing

- API endpoints were tested using Postman. A Postman collection is included with the project containing requests for all CRUD operations and service ticket mechanic assignments.
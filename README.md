## Mechanic Shop API

- The Mechanic Shop API is a Flask-based REST API for managing a mechanic shop's customers, mechanics, service tickets, and inventory. It uses SQLAlchemy for database management and token-based authentication for protected customer operations.

- The project includes Swagger API documentation and automated unit tests using Python's built-in unittest framework.



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
- Flask-Swagger / Flask-Swagger-UI
- Python unittest
- JWT or the token implementation used by the application

## Features

- Customers: Create accounts, log in, retrieve customer information, update accounts, and delete accounts.
- Mechanics: Create, retrieve, update, and delete mechanics, and view popular mechanics.
- Service Tickets: Create and retrieve service tickets, view a customer's tickets, assign or remove mechanics, edit mechanic assignments, and add inventory items.
- Inventory: Create, retrieve, update, and delete inventory items.
- Authentication: Generate and use authentication tokens for protected endpoints.
- Documentation: Document API endpoints, request payloads, and responses using Swagger.
- Testing: Test successful requests, validation errors, missing records, and authorization behavior.

## API Documentation
The API is documented using Swagger 2.0.

The Swagger specification is stored in swagger.yaml. It documents endpoint paths, HTTP methods, tags, summaries, request payloads, response schemas, and authentication requirements.

If Swagger UI is configured in the Flask application, open the configured Swagger UI URL in your browser. For example, the application may expose a documentation page at:

http://127.0.0.1:5000/api/docs

The exact URL depends on the Flask Swagger UI configuration.

If the documentation page does not load, verify that Swagger UI is registered with the application and that its specification URL points to the correct YAML file.

## Authentication
For protected endpoints, first log in using the customer login endpoint. Copy the returned token and use it in the Authorization header:

Authorization: Bearer YOUR_TOKEN
In Swagger UI, use the authorization control if it is configured for the bearerAuth security definition.

## Running the Tests
Run the full test suite from the project root:

python -m unittest discover tests

The test suite should cover all API routes, including successful requests and negative scenarios such as missing required fields, invalid credentials, nonexistent records, and unauthorized access.


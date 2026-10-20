from application import create_app
from application.models import db, ServiceTicket, Mechanic, Inventory, Customer
from application.utils.util import encode_token
from datetime import date
import unittest

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create the testing database tables first
        db.drop_all()
        db.create_all()
        # Create a customer before creating the service ticket
        self.customer = Customer(
            name="test_customer",
            email="customer@test.com",
            phone="1234567890",
            password="test"
        )

        db.session.add(self.customer)
        db.session.commit()
        # Create the service ticket using the real customer ID
        self.service_ticket = ServiceTicket(
            vin='test_vin',
            service_date=date(2026, 10, 15),
            service_desc='test_desc',
            customer_id=self.customer.id
        )
        
        
        db.session.add(self.service_ticket)
        db.session.commit()
            
        self.token = encode_token(self.customer.id)
        self.client = self.app.test_client()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_service_ticket(self):
        service_ticket_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2026-10-15",
           	"service_desc": "Oil change and brake inspection",
            "customer_id": self.customer.id
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['vin'], "1HGCM82633A123456")
        
    def test_invalid_creation(self):
        service_ticket_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2026-10-15",
            "customer_id": "1"
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['service_desc'], ['Missing data for required field.'])
        
    def test_assign_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="John",
                email="john@example.com",
                phone="5551234567",
                salary=50000
            )
            
            db.session.add(mechanic)
            db.session.commit()

            mechanic_id = mechanic.id
            service_ticket_id = self.service_ticket.id

        response = self.client.put(f'/service_tickets/{service_ticket_id}/assign_mechanic/{mechanic_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], f'Mechanic John assigned to service ticket {service_ticket_id}!')
        
    def test_assign_duplicate_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="John",
                email="john@example.com",
                phone="5551234567",
                salary=50000
            )
            
            db.session.add(mechanic)
            db.session.commit()
            
            service_ticket = db.session.get(ServiceTicket, self.service_ticket.id)

            service_ticket.mechanics.append(mechanic)
            db.session.commit()

            mechanic_id = mechanic.id
            service_ticket_id = self.service_ticket.id

        response = self.client.put(f'/service_tickets/{service_ticket_id}/assign_mechanic/{mechanic_id}')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'],'Mechanic is already assigned!')
        
    def test_remove_mechanic(self):
        with self.app.app_context():
            mechanic = Mechanic(
                name="John",
                email="john@example.com",
                phone="5551234567",
                salary=50000
            )

            db.session.add(mechanic)
            db.session.commit()

            service_ticket = db.session.get(ServiceTicket, self.service_ticket.id)

            service_ticket.mechanics.append(mechanic)
            db.session.commit()

            mechanic_id = mechanic.id
            service_ticket_id = service_ticket.id

        response = self.client.put(f'/service_tickets/{service_ticket_id}/remove_mechanic/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'],f'Successfully removed mechanic John from service ticket {service_ticket_id}')
        
        # Verify the relationship was removed
        with self.app.app_context():
            service_ticket = db.session.get(ServiceTicket, service_ticket_id)
            mechanic = db.session.get(Mechanic, mechanic_id)

            self.assertNotIn(mechanic, service_ticket.mechanics)
            
    def test_remove_invalid_mechanic(self):
        response = self.client.put(f'/service_tickets/{self.service_ticket.id}/remove_mechanic/9999')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid mechanic id.')
        
    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['vin'], 'test_vin')
        
    def test_get_my_tickets(self):
        with self.app.app_context():
            # Generate a token for the customer who owns the ticket
            customer_id = self.service_ticket.customer_id
            token = encode_token(customer_id)

        response = self.client.get('/service_tickets/my-tickets', headers={'Authorization': f'Bearer {token}'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['vin'], 'test_vin')
        self.assertEqual(response.json[0]['service_desc'], 'test_desc')
        
    def test_edit_ticket(self):
        with self.app.app_context():
            mechanic1 = Mechanic(
                name="John",
                email="john@example.com",
                phone="5551234567",
                salary=50000
            )

            mechanic2 = Mechanic(
                name="Jane",
                email="jane@example.com",
                phone="5559876543",
                salary=60000
            )

            db.session.add_all([mechanic1, mechanic2])
            db.session.commit()

            ticket = db.session.get(ServiceTicket, self.service_ticket.id)

            ticket.mechanics.append(mechanic1)
            db.session.commit()

            ticket_id = ticket.id
            mechanic1_id = mechanic1.id
            mechanic2_id = mechanic2.id

        payload = {
            "remove_ids": [mechanic1_id],
            "add_ids": [mechanic2_id]
        }

        response = self.client.put(
            f'/service_tickets/{ticket_id}/edit',
            json=payload
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['message'],
            'Service ticket updated successfully.'
        )

        # Verify the relationship changes were saved
        with self.app.app_context():
            ticket = db.session.get(ServiceTicket, ticket_id)
            mechanic1 = db.session.get(Mechanic, mechanic1_id)
            mechanic2 = db.session.get(Mechanic, mechanic2_id)

            self.assertNotIn(mechanic1, ticket.mechanics)
            self.assertIn(mechanic2, ticket.mechanics)
            
    def test_edit_invalid_ticket(self):
        payload = {
            "remove_ids": [],
            "add_ids": []
        }

        response = self.client.put(
            '/service_tickets/9999/edit',
            json=payload
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json['message'],
            'Invalid service ticket id.'
        )
        
    def test_add_inventory(self):
        with self.app.app_context():
            inventory = Inventory(
                name="Oil Filter",
                price=15.99
            )

            db.session.add(inventory)
            db.session.commit()

            inventory_id = inventory.id
            ticket_id = self.service_ticket.id

        response = self.client.put(
            f'/service_tickets/{ticket_id}/add_inventory/{inventory_id}'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['message'],
            f'Inventory item Oil Filter added to service ticket {ticket_id}!'
        )

        # Verify the relationship was saved
        with self.app.app_context():
            ticket = db.session.get(ServiceTicket, ticket_id)
            inventory = db.session.get(Inventory, inventory_id)

            self.assertIn(inventory, ticket.inventory)
        
    def test_add_invalid_inventory(self):
        response = self.client.put(
            f'/service_tickets/{self.service_ticket.id}/add_inventory/9999'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json['message'],
            'Invalid inventory id.'
        )
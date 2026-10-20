from app import create_app
from application.models import db, Customer
from application.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name='test_user', email='test@email.com', phone='test_phone', password='test')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
            
            customer_id = self.customer.id
            
        self.token = encode_token(customer_id)
        self.client = self.app.test_client()
        
    def test_create_customer(self):
        customer_payload = {
            "name": "Alice Wonderland",
            "email": "alice@email.com",
           	"phone": "123456789",
            "password": "password1234"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Alice Wonderland")
        
    def test_invalid_creation(self):
        customer_payload = {
            "name": "Alice Wonderland",
           	"phone": "123456789",
            "password": "password1234"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password!')
        
    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')
        
    def test_get_customer_by_id(self):
        response = self.client.get(f'/customers/{self.customer.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_user')
        
    def test_get_customer_not_found(self):
        response = self.client.get('/customers/9999')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Customer not found.')
        
    def test_update_customer(self):
        update_payload = {
            "name": "John"
        }
        
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.put(f'/customers/{self.customer.id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John')
        
    def test_update_customer_not_found(self):
        update_payload = {
            "name": "John"
        }

        headers = {
            'Authorization': "Bearer " + self.test_login_customer()
        }

        response = self.client.put('/customers/9999', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Customer not found.')
        
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        
        response = self.client.delete(f'/customers/{self.customer.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        
    def test_delete_customer_not_authorized(self):
        other_customer = Customer(
            name='other_user',
            email='other@email.com',
            phone='987654321',
            password='password123'
        )

        with self.app.app_context():
            db.session.add(other_customer)
            db.session.commit()
            other_customer_id = other_customer.id

        # Log in as the original test customer
        headers = {'Authorization': "Bearer " + self.test_login_customer()}

        # Try to delete the other customer's account
        response = self.client.delete(f'/customers/{other_customer_id}', headers=headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json['error'], "You are not authorized to delete this customer.")
from application import create_app
from application.models import db, Mechanic
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize the testing database
        db.drop_all()
        db.create_all()
        
        # Create a mechanic for the tests
        self.mechanic = Mechanic(
            name='test_mechanic',
            email='test@email.com',
            phone='1234567890',
            salary=65000.0
        )
        
        db.session.add(self.mechanic)
        db.session.commit()
    
        self.mechanic_id = self.mechanic.id
        self.client = self.app.test_client()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Smith",
            "email": "john@email.com",
           	"phone": "1234567890",
            "salary": 65000.0
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Smith")
        
    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            "name": "John Smith",
            "phone": "1234567890",
            "salary": 65000
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
        
    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
        
    def test_update_mechanic(self):
        update_payload = {
            "name": "John White"
        }
        
        response = self.client.put(f'/mechanics/{self.mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John White')
        
    def test_update_mechanic_not_found(self):
        update_payload = {
            "name": "John White"
        }

        response = self.client.put('/mechanics/9999', json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Mechanic not found.')
        
    def test_delete_mechanic(self):
        
        response = self.client.delete(f'/mechanics/{self.mechanic_id}')
        self.assertEqual(response.status_code, 200)
        
    def test_delete_mechanic_not_found(self):
        
        response = self.client.delete(f'/mechanics/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Mechanic not found.')
        
    def test_popular_mechanics(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')
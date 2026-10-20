from application import create_app
from application.models import db, Inventory
import unittest

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        
        self.inventory = Inventory(
            name='test_inventory',
            price=99.99
        )
        
        db.session.add(self.inventory)
        db.session.commit()
        
        self.inventory_id = self.inventory.id
        self.client = self.app.test_client()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_inventory(self):
        inventory_payload = {
            "name": "Engine Oil",
            "price": 29.99
        }

        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Engine Oil")
        
    def test_invalid_create_inventory(self):
        inventory_payload = {
            "name": "Engine Oil"
        }

        response = self.client.post('/inventory/', json=inventory_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
        
    def test_get_all_inventory(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_inventory')
        
    def test_get_inventory_by_id(self):
        response = self.client.get(f'/inventory/{self.inventory_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_inventory')
        
    def test_get_inventory_not_found(self):
        
        response = self.client.delete(f'/inventory/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')
        
    def test_update_inventory(self):
        update_payload = {
            "price": 39.99
        }
        
        response = self.client.put(f'/inventory/{self.inventory_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['price'],'39.99')
        
    def test_update_inventory_not_found(self):
        update_payload = {
            "name": "Air Filter"
        }

        response = self.client.put('/inventory/9999', json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')
        
    def test_delete_inventory(self):
        
        response = self.client.delete(f'/inventory/{self.inventory_id}')
        self.assertEqual(response.status_code, 200)
        
    def test_delete_inventory_not_found(self):
        
        response = self.client.delete(f'/inventory/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Inventory item not found.')
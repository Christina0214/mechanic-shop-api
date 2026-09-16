from application.extensions import ma
from application.models import ServiceTicket
from marshmallow import Schema, fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_fk = True
        
class EditServiceTicketSchema(Schema):
    add_ids = fields.List(fields.Integer(), required=False, load_default=[])
    remove_ids = fields.List(fields.Integer(), required=False, load_default=[])
        
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List

#Create a base class for our models
class Base(DeclarativeBase):
    pass
 
#Instantiate your SQLAlchemy database
db = SQLAlchemy(model_class = Base)

#Association Table
service_mechanic = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column("ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"), primary_key=True)
)

#Association Table
service_ticket_inventory = db.Table(
    "service_ticket_inventory",
    Base.metadata,
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.ForeignKey("inventory.id"), primary_key=True)
)

class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    #One-to-Many: Customer -> ServiceTicket
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(back_populates="customer")
    
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(360), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))
    #Many-to-One: ServiceTicket -> Customer
    customer: Mapped["Customer"] = db.relationship(back_populates="service_tickets")
    #Many-to-Many: ServiceTicket <-> Mechanic
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=service_mechanic, back_populates="service_tickets")
    #Many-to-Many: ServiceTicket <-> Inventory
    inventory: Mapped[List["Inventory"]] = db.relationship(secondary=service_ticket_inventory, back_populates="service_tickets")
    
class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=False)
    salary: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    
    #Many-to-Many: Mechanic <-> ServiceTicket
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_mechanic, back_populates="mechanics")
    
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    
    #Many-to-Many: Inventory <-> ServiceTicket
    service_tickets: Mapped[List["ServiceTicket"]] = db.relationship(secondary=service_ticket_inventory, back_populates="inventory")
"""
SQLAlchemy Relational ORM Models for RetailPulse.
Defines normalized schemas with primary keys, foreign keys, indexes, and constraints.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from src.database.connection import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, index=True)
    signup_date = Column(String(32), nullable=False, index=True)
    country = Column(String(64), nullable=False, index=True)
    region = Column(String(64), nullable=False, index=True)
    acquisition_channel = Column(String(64), nullable=False, index=True)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(32), primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    subcategory = Column(String(64), nullable=False, index=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    launch_date = Column(String(32), nullable=False)

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    returns = relationship("Return", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(32), primary_key=True, index=True)
    customer_id = Column(String(32), ForeignKey("customers.customer_id"), nullable=False, index=True)
    order_date = Column(String(32), nullable=False, index=True)
    order_status = Column(String(32), nullable=False, index=True)
    shipping_region = Column(String(64), nullable=False, index=True)
    payment_method = Column(String(64), nullable=False)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    total_items = Column(Integer, default=1)
    unique_products = Column(Integer, default=1)
    estimated_profit = Column(Float, default=0.0)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    returns = relationship("Return", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(String(32), primary_key=True, index=True)
    order_id = Column(String(32), ForeignKey("orders.order_id"), nullable=False, index=True)
    product_id = Column(String(32), ForeignKey("products.product_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    product_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    gross_amount = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(String(32), primary_key=True, index=True)
    order_id = Column(String(32), ForeignKey("orders.order_id"), nullable=False, index=True)
    payment_date = Column(String(32), nullable=False)
    payment_method = Column(String(64), nullable=False)
    payment_status = Column(String(32), nullable=False, index=True)
    payment_amount = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="payments")


class Return(Base):
    __tablename__ = "returns"

    return_id = Column(String(32), primary_key=True, index=True)
    order_id = Column(String(32), ForeignKey("orders.order_id"), nullable=False, index=True)
    product_id = Column(String(32), ForeignKey("products.product_id"), nullable=False, index=True)
    return_date = Column(String(32), nullable=False)
    return_reason = Column(String(128), nullable=False)
    refund_amount = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="returns")
    product = relationship("Product", back_populates="returns")


# Composite indexes for high-frequency analytical queries
Index("ix_orders_date_status_region", Order.order_date, Order.order_status, Order.shipping_region)
Index("ix_order_items_order_product", OrderItem.order_id, OrderItem.product_id)
Index("ix_returns_order_product", Return.order_id, Return.product_id)

"""Database package for RetailPulse."""
from src.database.connection import engine, get_db, get_db_session, check_db_connection, Base
from src.database.models import Customer, Product, Order, OrderItem, Payment, Return
from src.database.loader import DatabaseLoader

__all__ = [
    "engine",
    "get_db",
    "get_db_session",
    "check_db_connection",
    "Base",
    "Customer",
    "Product",
    "Order",
    "OrderItem",
    "Payment",
    "Return",
    "DatabaseLoader",
    "initialize_database",
    "inspect_warehouse_state",
]


def __getattr__(name: str):
    """Lazily exports initializer functions without eager circular package loading."""
    if name in ("initialize_database", "inspect_warehouse_state", "REQUIRED_TABLES", "REQUIRED_VIEWS"):
        import src.database.initializer as init_mod
        return getattr(init_mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


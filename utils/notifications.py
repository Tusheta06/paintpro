"""
PaintPro Inventory Management System
=====================================
Notifications Utility  |  utils/notifications.py

Generates dynamic system alerts for low stock, overdue invoices, etc.
"""

from database.connection import execute_query
from datetime import date

def get_system_notifications() -> list[dict]:
    """
    Returns a list of notification dictionaries.
    Types: 'danger', 'warning', 'info'
    """
    notifications = []
    
    # 1. Low Stock Alerts
    low_stock = execute_query(
        """
        SELECT sku, name, current_stock, minimum_stock 
        FROM vw_product_summary 
        WHERE stock_status IN ('low_stock', 'out_of_stock')
        """
    )
    for item in low_stock:
        if item['current_stock'] <= 0:
            notifications.append({
                "type": "danger",
                "icon": "fa-triangle-exclamation",
                "title": "Out of Stock",
                "message": f"Product '{item['name']}' (SKU: {item['sku']}) is completely out of stock.",
                "action_link": "purchases"
            })
        else:
            notifications.append({
                "type": "warning",
                "icon": "fa-battery-quarter",
                "title": "Low Stock",
                "message": f"Product '{item['name']}' is running low (Current: {item['current_stock']:g}, Min: {item['minimum_stock']:g}).",
                "action_link": "purchases"
            })
            
    # 2. Unpaid/Overdue Invoices
    today = date.today()
    overdue_sales = execute_query(
        """
        SELECT invoice_number, due_date, grand_total, c.name as customer_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.payment_status != 'paid' AND s.status != 'cancelled'
        """
    )
    for sale in overdue_sales:
        # Check if due date is passed
        due = sale['due_date']
        if due and due < today:
            days_overdue = (today - due).days
            notifications.append({
                "type": "danger",
                "icon": "fa-file-invoice-dollar",
                "title": "Overdue Invoice",
                "message": f"Invoice {sale['invoice_number']} for {sale['customer_name']} is {days_overdue} days overdue.",
                "action_link": "sales"
            })
        elif due and (due - today).days <= 3:
            notifications.append({
                "type": "warning",
                "icon": "fa-clock",
                "title": "Invoice Due Soon",
                "message": f"Invoice {sale['invoice_number']} for {sale['customer_name']} is due in {(due - today).days} days.",
                "action_link": "sales"
            })
            
    # 3. Pending Purchase Orders
    pending_pos = execute_query(
        """
        SELECT po_number, expected_date, s.name as supplier_name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.status = 'ordered'
        """
    )
    for po in pending_pos:
        exp = po['expected_date']
        if exp and exp < today:
            notifications.append({
                "type": "warning",
                "icon": "fa-truck-fast",
                "title": "Delayed Delivery",
                "message": f"PO {po['po_number']} from {po['supplier_name']} was expected on {exp.strftime('%b %d')} and is delayed.",
                "action_link": "purchases"
            })
        else:
            notifications.append({
                "type": "info",
                "icon": "fa-truck",
                "title": "Inbound Shipment",
                "message": f"PO {po['po_number']} from {po['supplier_name']} is currently in transit.",
                "action_link": "purchases"
            })
            
    # Sort: danger first, then warning, then info
    priority = {"danger": 0, "warning": 1, "info": 2}
    notifications.sort(key=lambda x: priority.get(x["type"], 3))
    
    return notifications

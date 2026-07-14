"""
PaintPro Inventory Management System
=====================================
Customer Model (DAO)  |  models/customer.py

Data access object for the customers table.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import log_activity

class CustomerModel:
    
    @staticmethod
    def get_all(search_query: str = "", customer_type: str = None) -> list[dict]:
        """Fetch all active customers, optionally filtered."""
        sql = "SELECT * FROM customers WHERE is_active = 1"
        params = []
        
        if search_query:
            sql += " AND (name LIKE %s OR phone LIKE %s OR email LIKE %s OR gst_number LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val, val, val])
            
        if customer_type and customer_type != "All":
            sql += " AND customer_type = %s"
            params.append(customer_type.lower())
            
        sql += " ORDER BY name ASC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(customer_id: int) -> dict:
        """Fetch a single customer by ID."""
        return execute_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
        
    @staticmethod
    def create(data: dict, user_id: int) -> tuple[bool, str]:
        """Create a new customer."""
        try:
            # Phone duplication check (often used as primary identifier for retail)
            if data.get("phone"):
                existing = execute_one("SELECT id FROM customers WHERE phone = %s AND is_active = 1", (data["phone"],))
                if existing:
                    return False, f"A customer with phone '{data['phone']}' already exists."
                    
            if data.get("gst_number"):
                existing_gst = execute_one("SELECT id FROM customers WHERE gst_number = %s AND is_active = 1", (data["gst_number"],))
                if existing_gst:
                    return False, f"A customer with GST '{data['gst_number']}' already exists."
                    
            cols = list(data.keys())
            cols.append("created_by")
            
            vals = list(data.values())
            vals.append(user_id)
            
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            
            sql = f"INSERT INTO customers ({col_names}) VALUES ({placeholders})"
            new_id = execute_write(sql, tuple(vals), return_last_id=True)
            
            log_activity("create_customer", "business", f"Created customer {data['name']}", user_id=user_id, entity_id=new_id)
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def update(customer_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Update an existing customer."""
        try:
            if data.get("phone"):
                existing = execute_one("SELECT id FROM customers WHERE phone = %s AND id != %s AND is_active = 1", (data["phone"], customer_id))
                if existing:
                    return False, f"A customer with phone '{data['phone']}' already exists."
                    
            if data.get("gst_number"):
                existing_gst = execute_one("SELECT id FROM customers WHERE gst_number = %s AND id != %s AND is_active = 1", (data["gst_number"], customer_id))
                if existing_gst:
                    return False, f"A customer with GST '{data['gst_number']}' already exists."
                    
            updates = []
            vals = []
            for k, v in data.items():
                updates.append(f"{k} = %s")
                vals.append(v)
                
            vals.append(customer_id)
            sql = f"UPDATE customers SET {', '.join(updates)} WHERE id = %s"
            
            execute_write(sql, tuple(vals))
            log_activity("update_customer", "business", f"Updated customer ID {customer_id}", user_id=user_id, entity_id=customer_id)
            
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def delete(customer_id: int, user_id: int) -> tuple[bool, str]:
        """Soft delete a customer (only if no sales are linked)."""
        try:
            linked = execute_one("SELECT COUNT(*) as cnt FROM sales WHERE customer_id = %s", (customer_id,))
            if linked and linked['cnt'] > 0:
                return False, f"Cannot delete: {linked['cnt']} sales records exist for this customer."
                
            execute_write("UPDATE customers SET is_active = 0 WHERE id = %s", (customer_id,))
            log_activity("delete_customer", "business", f"Deleted customer ID {customer_id}", user_id=user_id, entity_id=customer_id)
            return True, ""
        except Exception as e:
            return False, str(e)

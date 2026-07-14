"""
PaintPro Inventory Management System
=====================================
Supplier Model (DAO)  |  models/supplier.py

Data access object for the suppliers table.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import log_activity

class SupplierModel:
    
    @staticmethod
    def get_all(search_query: str = "") -> list[dict]:
        """Fetch all active suppliers."""
        sql = "SELECT * FROM suppliers WHERE is_active = 1"
        params = []
        
        if search_query:
            sql += " AND (name LIKE %s OR contact_person LIKE %s OR phone LIKE %s OR email LIKE %s OR gst_number LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val, val, val, val])
            
        sql += " ORDER BY name ASC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(supplier_id: int) -> dict:
        """Fetch a single supplier by ID."""
        return execute_one("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
        
    @staticmethod
    def create(data: dict, user_id: int) -> tuple[bool, str]:
        """Create a new supplier."""
        try:
            # Name duplication check
            existing = execute_one("SELECT id FROM suppliers WHERE name = %s AND is_active = 1", (data["name"],))
            if existing:
                return False, f"A supplier with name '{data['name']}' already exists."
                
            # GST duplication check (if provided)
            if data.get("gst_number"):
                existing_gst = execute_one("SELECT id FROM suppliers WHERE gst_number = %s AND is_active = 1", (data["gst_number"],))
                if existing_gst:
                    return False, f"A supplier with GST '{data['gst_number']}' already exists."
                    
            cols = list(data.keys())
            cols.append("created_by")
            
            vals = list(data.values())
            vals.append(user_id)
            
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            
            sql = f"INSERT INTO suppliers ({col_names}) VALUES ({placeholders})"
            new_id = execute_write(sql, tuple(vals), return_last_id=True)
            
            log_activity("create_supplier", "business", f"Created supplier {data['name']}", user_id=user_id, entity_id=new_id)
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def update(supplier_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Update an existing supplier."""
        try:
            if "name" in data:
                existing = execute_one("SELECT id FROM suppliers WHERE name = %s AND id != %s AND is_active = 1", (data["name"], supplier_id))
                if existing:
                    return False, f"A supplier with name '{data['name']}' already exists."
                    
            if data.get("gst_number"):
                existing_gst = execute_one("SELECT id FROM suppliers WHERE gst_number = %s AND id != %s AND is_active = 1", (data["gst_number"], supplier_id))
                if existing_gst:
                    return False, f"A supplier with GST '{data['gst_number']}' already exists."
                    
            updates = []
            vals = []
            for k, v in data.items():
                updates.append(f"{k} = %s")
                vals.append(v)
                
            vals.append(supplier_id)
            sql = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = %s"
            
            execute_write(sql, tuple(vals))
            log_activity("update_supplier", "business", f"Updated supplier ID {supplier_id}", user_id=user_id, entity_id=supplier_id)
            
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def delete(supplier_id: int, user_id: int) -> tuple[bool, str]:
        """Soft delete a supplier (only if no purchases are linked)."""
        try:
            linked = execute_one("SELECT COUNT(*) as cnt FROM purchases WHERE supplier_id = %s", (supplier_id,))
            if linked and linked['cnt'] > 0:
                return False, f"Cannot delete: {linked['cnt']} purchases exist for this supplier."
                
            execute_write("UPDATE suppliers SET is_active = 0 WHERE id = %s", (supplier_id,))
            log_activity("delete_supplier", "business", f"Deleted supplier ID {supplier_id}", user_id=user_id, entity_id=supplier_id)
            return True, ""
        except Exception as e:
            return False, str(e)

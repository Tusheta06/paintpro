"""
PaintPro Inventory Management System
=====================================
Brand Model (DAO)  |  models/brand.py

Data access object for the brands table.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import log_activity

class BrandModel:
    
    @staticmethod
    def get_all(search_query: str = "") -> list[dict]:
        """Fetch all active brands."""
        sql = "SELECT * FROM brands WHERE is_active = 1"
        params = []
        
        if search_query:
            sql += " AND (name LIKE %s OR description LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val])
            
        sql += " ORDER BY name ASC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(brand_id: int) -> dict:
        """Fetch a single brand by ID."""
        return execute_one("SELECT * FROM brands WHERE id = %s", (brand_id,))
        
    @staticmethod
    def create(data: dict, user_id: int) -> tuple[bool, str]:
        """Create a new brand."""
        try:
            existing = execute_one("SELECT id FROM brands WHERE name = %s AND is_active = 1", (data["name"],))
            if existing:
                return False, f"A brand with name '{data['name']}' already exists."
                
            execute_write(
                "INSERT INTO brands (name, slug, description, created_by) VALUES (%s, %s, %s, %s)",
                (
                    data["name"],
                    data["name"].lower().replace(" ", "-"),
                    data.get("description"),
                    user_id,
                )
            )
            log_activity("create_brand", "inventory", f"Created brand {data['name']}", user_id=user_id)
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def update(brand_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Update an existing brand."""
        try:
            if "name" in data:
                existing = execute_one("SELECT id FROM brands WHERE name = %s AND id != %s AND is_active = 1", (data["name"], brand_id))
                if existing:
                    return False, f"A brand with name '{data['name']}' already exists."
                    
            updates = []
            vals = []
            for k, v in data.items():
                updates.append(f"{k} = %s")
                vals.append(v)
                
            vals.append(brand_id)
            sql = f"UPDATE brands SET {', '.join(updates)} WHERE id = %s"
            
            execute_write(sql, tuple(vals))
            log_activity("update_brand", "inventory", f"Updated brand ID {brand_id}", user_id=user_id, entity_id=brand_id)
            
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def delete(brand_id: int, user_id: int) -> tuple[bool, str]:
        """Soft delete a brand (only if no products are linked)."""
        try:
            linked = execute_one("SELECT COUNT(*) as cnt FROM products WHERE brand_id = %s AND is_active = 1", (brand_id,))
            if linked and linked['cnt'] > 0:
                return False, f"Cannot delete: {linked['cnt']} active products are using this brand."
                
            execute_write("UPDATE brands SET is_active = 0 WHERE id = %s", (brand_id,))
            log_activity("delete_brand", "inventory", f"Deleted brand ID {brand_id}", user_id=user_id, entity_id=brand_id)
            return True, ""
        except Exception as e:
            return False, str(e)

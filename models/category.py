"""
PaintPro Inventory Management System
=====================================
Category Model (DAO)  |  models/category.py

Data access object for the categories table.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import log_activity

class CategoryModel:
    
    @staticmethod
    def get_all(search_query: str = "") -> list[dict]:
        """Fetch all active categories."""
        sql = "SELECT * FROM categories WHERE is_active = 1"
        params = []
        
        if search_query:
            sql += " AND (name LIKE %s OR description LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val])
            
        sql += " ORDER BY name ASC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(category_id: int) -> dict:
        """Fetch a single category by ID."""
        return execute_one("SELECT * FROM categories WHERE id = %s", (category_id,))
        
    @staticmethod
    def create(data: dict, user_id: int) -> tuple[bool, str]:
        """Create a new category."""
        try:
            # Check for duplicate name
            existing = execute_one("SELECT id FROM categories WHERE name = %s AND is_active = 1", (data["name"],))
            if existing:
                return False, f"A category with name '{data['name']}' already exists."
                
            execute_write(
                "INSERT INTO categories (name, slug, description, created_by) VALUES (%s, %s, %s, %s)",
                (
                    data["name"],
                    data["name"].lower().replace(" ", "-"),
                    data.get("description"),
                    user_id
                )
            )
            log_activity("create_category", "inventory", f"Created category {data['name']}", user_id=user_id)
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def update(category_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Update an existing category."""
        try:
            # Check for duplicate name
            if "name" in data:
                existing = execute_one("SELECT id FROM categories WHERE name = %s AND id != %s AND is_active = 1", (data["name"], category_id))
                if existing:
                    return False, f"A category with name '{data['name']}' already exists."
                    
            updates = []
            vals = []
            for k, v in data.items():
                updates.append(f"{k} = %s")
                vals.append(v)
                
            vals.append(category_id)
            sql = f"UPDATE categories SET {', '.join(updates)} WHERE id = %s"
            
            execute_write(sql, tuple(vals))
            log_activity("update_category", "inventory", f"Updated category ID {category_id}", user_id=user_id, entity_id=category_id)
            
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def delete(category_id: int, user_id: int) -> tuple[bool, str]:
        """Soft delete a category (only if no products are linked)."""
        try:
            # Check for linked products
            linked = execute_one("SELECT COUNT(*) as cnt FROM products WHERE category_id = %s AND is_active = 1", (category_id,))
            if linked and linked['cnt'] > 0:
                return False, f"Cannot delete: {linked['cnt']} active products are using this category."
                
            execute_write("UPDATE categories SET is_active = 0 WHERE id = %s", (category_id,))
            log_activity("delete_category", "inventory", f"Deleted category ID {category_id}", user_id=user_id, entity_id=category_id)
            return True, ""
        except Exception as e:
            return False, str(e)

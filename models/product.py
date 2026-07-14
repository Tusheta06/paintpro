"""
PaintPro Inventory Management System
=====================================
Product Model (DAO)  |  models/product.py

Data access object for the products table.
"""

from database.connection import execute_query, execute_one, execute_write
from utils.auth import log_activity
import streamlit as st

class ProductModel:
    
    @staticmethod
    def get_all(search_query: str = "", category_id: int = None, brand_id: int = None) -> list[dict]:
        """Fetch all active products, optionally filtered."""
        sql = "SELECT * FROM vw_product_summary WHERE is_active = 1"
        params = []
        
        if search_query:
            sql += " AND (name LIKE %s OR sku LIKE %s OR color_name LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val, val])
            
        if category_id:
            sql += " AND category_id = %s"
            params.append(category_id)
            
        if brand_id:
            sql += " AND brand_id = %s"
            params.append(brand_id)
            
        sql += " ORDER BY name ASC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(product_id: int) -> dict:
        """Fetch a single product by ID (full details from raw table)."""
        return execute_one("SELECT * FROM products WHERE id = %s", (product_id,))
        
    @staticmethod
    def create(data: dict, user_id: int) -> tuple[bool, str]:
        """Create a new product."""
        try:
            # Check for duplicate SKU
            existing = execute_one("SELECT id FROM products WHERE sku = %s", (data["sku"],))
            if existing:
                return False, f"A product with SKU '{data['sku']}' already exists."
                
            cols = list(data.keys())
            cols.append("created_by")
            
            vals = list(data.values())
            vals.append(user_id)
            
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            
            sql = f"INSERT INTO products ({col_names}) VALUES ({placeholders})"
            new_id = execute_write(sql, tuple(vals), return_last_id=True)
            
            # Log initial stock as an opening balance if > 0
            if data.get("current_stock", 0) > 0:
                execute_write(
                    """
                    INSERT INTO stock_logs (product_id, user_id, reference_type, quantity_change, quantity_after, notes)
                    VALUES (%s, %s, 'opening', %s, %s, 'Initial opening stock')
                    """,
                    (new_id, user_id, data["current_stock"], data["current_stock"])
                )
                
            log_activity("create_product", "inventory", f"Created product {data.get('name')} (SKU: {data.get('sku')})", user_id=user_id, entity_id=new_id)
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def update(product_id: int, data: dict, user_id: int) -> tuple[bool, str]:
        """Update an existing product."""
        try:
            # Check for duplicate SKU (excluding self)
            if "sku" in data:
                existing = execute_one("SELECT id FROM products WHERE sku = %s AND id != %s", (data["sku"], product_id))
                if existing:
                    return False, f"A product with SKU '{data['sku']}' already exists."
                    
            # We don't update current_stock directly through this method, 
            # stock updates should go through stock_management module to track logs.
            if "current_stock" in data:
                del data["current_stock"]
                
            updates = []
            vals = []
            for k, v in data.items():
                updates.append(f"{k} = %s")
                vals.append(v)
                
            vals.append(product_id)
            sql = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
            
            execute_write(sql, tuple(vals))
            log_activity("update_product", "inventory", f"Updated product ID {product_id}", user_id=user_id, entity_id=product_id)
            
            return True, ""
        except Exception as e:
            return False, str(e)
            
    @staticmethod
    def delete(product_id: int, user_id: int) -> tuple[bool, str]:
        """Soft delete a product."""
        try:
            execute_write("UPDATE products SET is_active = 0 WHERE id = %s", (product_id,))
            log_activity("delete_product", "inventory", f"Deleted product ID {product_id}", user_id=user_id, entity_id=product_id)
            return True, ""
        except Exception as e:
            return False, str(e)

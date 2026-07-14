"""
PaintPro Inventory Management System
=====================================
Purchase Model (DAO)  |  models/purchase.py

Data access object for managing purchase orders and their line items.
Includes transaction management for atomic operations.
"""

from database.connection import execute_query, execute_one, execute_write, get_connection
from utils.auth import log_activity
from mysql.connector import Error

class PurchaseModel:
    
    @staticmethod
    def get_all(search_query: str = "", status: str = None) -> list[dict]:
        """Fetch all purchase orders."""
        sql = """
        SELECT
            p.*,
            s.name AS supplier_name,
            u.full_name AS created_by_name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN users u ON p.created_by = u.id
        WHERE 1=1
    """
        params = []
        
        if search_query:
            sql += " AND (p.po_number LIKE %s OR s.name LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val])
            
        if status and status != "All":
            sql += " AND p.status = %s"
            params.append(status.lower())
            
        sql += " ORDER BY p.created_at DESC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(purchase_id: int) -> dict:
        """Fetch a single purchase order header."""
        return execute_one(
            """
            SELECT p.*, s.name as supplier_name 
            FROM purchases p 
            LEFT JOIN suppliers s ON p.supplier_id = s.id 
            WHERE p.id = %s
            """, 
            (purchase_id,)
        )
        
    @staticmethod
    def get_items(purchase_id: int) -> list[dict]:
        """Fetch line items for a purchase order."""
        return execute_query(
        """
        SELECT 
            pi.id,
            pi.purchase_id,
            pi.product_id,
            p.name AS product_name,
            p.sku,
            pi.quantity_ordered AS quantity,
            pi.quantity_received,
            pi.unit_cost,
            pi.gst_percentage,
            pi.gst_amount,
            pi.discount_percentage,
            pi.discount_amount,
            pi.line_total AS total_cost
        FROM purchase_items pi
        JOIN products p ON pi.product_id = p.id
        WHERE pi.purchase_id = %s
        """,
        (purchase_id,)
    )

    @staticmethod
    def create_with_items(header_data: dict, items: list[dict], user_id: int) -> tuple[bool, str]:
        """
        Create a purchase order and its line items inside a database transaction.
        """
        conn, cursor = None, None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction()

            # Insert Header
            cols = list(header_data.keys())
            cols.append("created_by")

            vals = list(header_data.values())
            vals.append(user_id)

            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)

            sql_header = f"INSERT INTO purchases ({col_names}) VALUES ({placeholders})"
            cursor.execute(sql_header, tuple(vals))
            purchase_id = cursor.lastrowid

            # Insert Items
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO purchase_items (
                        purchase_id,
                        product_id,
                        quantity_ordered,
                        quantity_received,
                        unit_cost,
                        gst_percentage,
                        gst_amount,
                        discount_percentage,
                        discount_amount,
                        line_total
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        purchase_id,
                        item["product_id"],
                        item["quantity"],
                        0,
                        item["unit_cost"],
                        0,
                        0,
                        0,
                        0,
                        item["total_cost"]
                    )
                )

            conn.commit()

            log_activity(
                "create_purchase",
                "purchases",
                f"Created PO #{purchase_id}",
                user_id=user_id,
                entity_id=purchase_id
            )

            return True, str(purchase_id)

        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Database Error: {e}"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            
    @staticmethod
    def update_status(purchase_id: int, new_status: str, payment_status: str, user_id: int) -> tuple[bool, str]:
        """Update the status of a PO. Triggers handle stock updates if status='received'."""
        try:
            # First check current status
            curr = execute_one("SELECT status FROM purchases WHERE id = %s", (purchase_id,))
            if not curr:
                return False, "Purchase order not found."
            if curr['status'] == 'received' and new_status != 'received':
                # Our simple trigger logic only handles INCOMING stock on received. 
                # Reverting requires careful stock deduction which our basic triggers don't do.
                return False, "Cannot change status from 'received' as stock has already been updated."
                
            execute_write(
                "UPDATE purchases SET status = %s, payment_status = %s WHERE id = %s",
                (new_status, payment_status, purchase_id)
            )
            log_activity("update_purchase_status", "purchases", f"Updated PO #{purchase_id} to {new_status}", user_id=user_id, entity_id=purchase_id)
            return True, ""
        except Exception as e:
            return False, str(e)

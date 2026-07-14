"""
PaintPro Inventory Management System
=====================================
Sale Model (DAO)  |  models/sale.py

Data access object for managing sales and their line items.
Includes transaction management for atomic operations.
"""


from database.connection import execute_query, execute_one, execute_write, get_connection
from utils.auth import log_activity
from mysql.connector import Error

class SaleModel:
    
    @staticmethod
    def get_all(search_query: str = "", status: str = None) -> list[dict]:
        """Fetch all sales invoices."""
        sql = """
            SELECT
                s.*,
                c.name AS customer_name,
                u.full_name AS created_by_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            LEFT JOIN users u ON s.created_by = u.id
            WHERE 1=1
"""
        params = []
        
        if search_query:
            sql += " AND (s.invoice_number LIKE %s OR c.name LIKE %s)"
            val = f"%{search_query}%"
            params.extend([val, val])
            
        if status and status != "All":
            sql += " AND s.status = %s"
            params.append(status.lower())
            
        sql += " ORDER BY s.created_at DESC"
        return execute_query(sql, tuple(params))
        
    @staticmethod
    def get_by_id(sale_id: int) -> dict:
        """Fetch a single sale header."""
        return execute_one(
            """
            SELECT
                s.*,
                c.name AS customer_name,
                CONCAT_WS(', ',
                    c.address_line1,
                    c.address_line2,
                    c.city,
                    c.state,
                    c.pincode
                ) AS customer_address,
                c.gst_number AS customer_gst,
                c.phone AS customer_phone
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = %s
            """,
            (sale_id,)
        )
        
    @staticmethod
    def get_items(sale_id: int) -> list[dict]:
        """Fetch line items for a sale."""
        return execute_query(
            """
            SELECT si.*, p.name as product_name, p.sku, p.gst_percentage 
            FROM sale_items si 
            JOIN products p ON si.product_id = p.id 
            WHERE si.sale_id = %s
            """, 
            (sale_id,)
        )
        
    @staticmethod
    def create_with_items(header_data: dict, items: list[dict], user_id: int) -> tuple[bool, str]:
        """
        Create a sale and its line items inside a database transaction.
        Stock deduction is automatically handled by the database trigger `after_sales_item_insert`.
        """
        conn, cursor = None, None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction()
            
            # 1. Check stock availability before inserting
            for item in items:
                cursor.execute("SELECT current_stock, name FROM products WHERE id = %s", (item['product_id'],))
                prod = cursor.fetchone()
                if not prod:
                    raise Exception(f"Product ID {item['product_id']} not found.")
                if prod['current_stock'] < item['quantity']:
                    raise Exception(f"Insufficient stock for '{prod['name']}'. Available: {prod['current_stock']}, Requested: {item['quantity']}")
            
            # 2. Insert Header
            cols = list(header_data.keys())
            cols.append("created_by")
            vals = list(header_data.values())
            vals.append(user_id)
            
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            
            sql_header = f"INSERT INTO sales ({col_names}) VALUES ({placeholders})"
            cursor.execute(sql_header, tuple(vals))
            sale_id = cursor.lastrowid
            
            # 3. Insert Items (Triggers stock deduction automatically)
            for item in items:
                cursor.execute(
                    """
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (sale_id, item['product_id'], item['quantity'], item['unit_price'], item.get('discount', 0), item['total_price'])
                )
                
            conn.commit()
            log_activity("create_sale", "sales", f"Created Invoice for Sale #{sale_id}", user_id=user_id, entity_id=sale_id)
            return True, str(sale_id)
            
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Database Error: {e}"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, str(e)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    @staticmethod
    def update_status(sale_id: int, new_status: str, payment_status: str, user_id: int) -> tuple[bool, str]:
        """Update the status of a Sale."""
        try:
            # We don't restore stock automatically on cancellation here for simplicity,
            # in a full production system, cancelling a sale should increment stock back via triggers or code.
            execute_write(
                "UPDATE sales SET status = %s, payment_status = %s WHERE id = %s",
                (new_status, payment_status, sale_id)
            )
            log_activity("update_sale_status", "sales", f"Updated Sale #{sale_id} to {new_status}", user_id=user_id, entity_id=sale_id)
            return True, ""
        except Exception as e:
            return False, str(e)

"""
PaintPro Inventory Management System
=====================================
AI Predictive Analytics  |  utils/ai_predict.py

Algorithm to calculate sales velocity and predict days of inventory
remaining to provide proactive reorder alerts.
"""

from database.connection import execute_query
import pandas as pd
from datetime import date, timedelta

def get_predictive_stock_alerts(days_window: int = 30) -> pd.DataFrame:
    """
    Calculates predictive stock alerts based on recent sales velocity.
    
    Formula:
      Velocity = (Units sold in last X days) / X
      Days Remaining = Current Stock / Velocity
      
    Returns a DataFrame sorted by most critical items.
    """
    
    # 1. Fetch current stock for all active products
    products_sql = """
        SELECT id as product_id, sku, name, current_stock, minimum_stock, cost_price
        FROM products
        WHERE is_active = 1
    """
    products = execute_query(products_sql)
    
    if not products:
        return pd.DataFrame()
        
    df_prod = pd.DataFrame(products)
    
    # 2. Fetch sales velocity over the time window
    start_date = date.today() - timedelta(days=days_window)
    
    sales_sql = """
        SELECT si.product_id, SUM(si.quantity) as total_sold
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        WHERE s.status IN ('confirmed','delivered') AND DATE(s.invoice_date) >= %s
        GROUP BY si.product_id
    """
    sales = execute_query(sales_sql, (start_date,))
    
    if not sales:
        df_prod['daily_velocity'] = 0.0
        df_prod['days_remaining'] = float('inf')
        df_prod['ai_status'] = 'Safe'
        return df_prod
        
    df_sales = pd.DataFrame(sales)
    
  # 3. Merge and calculate
    df = pd.merge(df_prod, df_sales, on='product_id', how='left')
    print(df.dtypes)
    print(type(df.loc[0, 'current_stock']))
    print(type(df.loc[0, 'minimum_stock']))
    print(type(df.loc[0, 'cost_price']))
    print(type(df.loc[0, 'total_sold']))

# Fill missing sales values
    df['total_sold'] = df['total_sold'].fillna(0)

# Convert numeric columns from Decimal to float
    df['current_stock'] = pd.to_numeric(df['current_stock'], errors='coerce')
    df['minimum_stock'] = pd.to_numeric(df['minimum_stock'], errors='coerce')
    df['cost_price'] = pd.to_numeric(df['cost_price'], errors='coerce')
    df['total_sold'] = pd.to_numeric(df['total_sold'], errors='coerce')

# Calculate daily velocity
    df['daily_velocity'] = df['total_sold'] / days_window
    
    # Calculate days remaining (handle division by zero)
    df['days_remaining'] = df.apply(
        lambda row: (row['current_stock'] / row['daily_velocity']) if row['daily_velocity'] > 0 else float('inf'), 
        axis=1
    )
    
    # 4. Categorize AI Status
    def categorize_status(row):
        if row['current_stock'] <= 0:
            return 'Stockout'
        if row['days_remaining'] <= 14:
            return 'Critical (< 2 weeks)'
        if row['days_remaining'] <= 30:
            return 'Warning (< 1 month)'
        if row['current_stock'] <= row['minimum_stock']:
            return 'Below Minimum'
        return 'Safe'
        
    df['ai_status'] = df.apply(categorize_status, axis=1)
    
    # Calculate recommended order quantity (to reach 45 days supply)
    df['suggested_order_qty'] = df.apply(
        lambda row: max(0, int((row['daily_velocity'] * 45) - row['current_stock'])),
        axis=1
    )
    
    # Calculate investment needed for suggested order
    df['estimated_cost'] = df['suggested_order_qty'] * df['cost_price']
    
    # Sort: Stockouts first, then most critical days remaining
    df_sorted = df.sort_values(by=['days_remaining', 'current_stock'], ascending=[True, True])
    
    return df_sorted

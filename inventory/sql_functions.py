"""
Funciones SQL de PostgreSQL para casos de uso específicos
del método get_related
"""

# Función SQL para: "Productos de una marca que aparecen en órdenes de un cliente específico"
GET_PRODUCTS_BY_BRAND_AND_CUSTOMER_SQL = """
CREATE OR REPLACE FUNCTION get_products_by_brand_and_customer(
    brand_name_param VARCHAR,
    customer_email_param VARCHAR
)
RETURNS TABLE (
    product_id UUID,
    product_name VARCHAR,
    product_sku VARCHAR,
    product_price DECIMAL,
    brand_name VARCHAR,
    category_name VARCHAR,
    customer_name VARCHAR,
    customer_email VARCHAR,
    order_id UUID,
    order_status VARCHAR,
    order_date TIMESTAMP,
    qty_ordered INTEGER,
    unit_price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        p.id AS product_id,
        p.name AS product_name,
        p.sku AS product_sku,
        p.price AS product_price,
        b.name AS brand_name,
        c.name AS category_name,
        cu.full_name AS customer_name,
        cu.email AS customer_email,
        o.id AS order_id,
        o.status AS order_status,
        o.created_at AS order_date,
        oi.qty AS qty_ordered,
        oi.unit_price AS unit_price
    FROM 
        inventory_product p
        INNER JOIN inventory_brand b ON p.brand_id = b.id
        INNER JOIN inventory_category c ON p.category_id = c.id
        INNER JOIN inventory_orderitem oi ON p.id = oi.product_id
        INNER JOIN inventory_order o ON oi.order_id = o.id
        INNER JOIN inventory_customer cu ON o.customer_id = cu.id
    WHERE 
        b.name ILIKE '%' || brand_name_param || '%'
        AND cu.email = customer_email_param
        AND p.is_active = true
        AND b.is_active = true
    ORDER BY 
        p.name, o.created_at DESC;
END;
$$ LANGUAGE plpgsql;
"""

# Función SQL para: "Pagos donde se facturó un producto específico por más de X unidades"
GET_PAYMENTS_BY_PRODUCT_QUANTITY_SQL = """
CREATE OR REPLACE FUNCTION get_payments_by_product_quantity(
    product_sku_param VARCHAR,
    min_quantity INTEGER
)
RETURNS TABLE (
    payment_id UUID,
    payment_method VARCHAR,
    payment_amount DECIMAL,
    payment_status VARCHAR,
    payment_date TIMESTAMP,
    order_id UUID,
    customer_name VARCHAR,
    customer_email VARCHAR,
    product_name VARCHAR,
    product_sku VARCHAR,
    qty_ordered INTEGER,
    unit_price DECIMAL,
    total_product_amount DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        py.id AS payment_id,
        py.method AS payment_method,
        py.amount AS payment_amount,
        py.status AS payment_status,
        py.created_at AS payment_date,
        o.id AS order_id,
        c.full_name AS customer_name,
        c.email AS customer_email,
        p.name AS product_name,
        p.sku AS product_sku,
        oi.qty AS qty_ordered,
        oi.unit_price AS unit_price,
        (oi.qty * oi.unit_price) AS total_product_amount
    FROM 
        inventory_payment py
        INNER JOIN inventory_order o ON py.order_id = o.id
        INNER JOIN inventory_customer c ON o.customer_id = c.id
        INNER JOIN inventory_orderitem oi ON o.id = oi.order_id
        INNER JOIN inventory_product p ON oi.product_id = p.id
    WHERE 
        p.sku = product_sku_param
        AND oi.qty >= min_quantity
        AND py.status = 'CONFIRMED'
    ORDER BY 
        py.created_at DESC, oi.qty DESC;
END;
$$ LANGUAGE plpgsql;
"""

# Función SQL para análisis de stock por bodega
GET_STOCK_ANALYSIS_SQL = """
CREATE OR REPLACE FUNCTION get_stock_analysis(
    warehouse_name_param VARCHAR DEFAULT NULL,
    min_stock INTEGER DEFAULT 0
)
RETURNS TABLE (
    warehouse_name VARCHAR,
    warehouse_city VARCHAR,
    product_name VARCHAR,
    product_sku VARCHAR,
    brand_name VARCHAR,
    category_name VARCHAR,
    qty INTEGER,
    reserved INTEGER,
    available INTEGER,
    product_price DECIMAL,
    stock_value DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        w.name AS warehouse_name,
        w.city AS warehouse_city,
        p.name AS product_name,
        p.sku AS product_sku,
        b.name AS brand_name,
        cat.name AS category_name,
        s.qty AS qty,
        s.reserved AS reserved,
        (s.qty - s.reserved) AS available,
        p.price AS product_price,
        (s.qty * p.price) AS stock_value
    FROM 
        inventory_stock s
        INNER JOIN inventory_warehouse w ON s.warehouse_id = w.id
        INNER JOIN inventory_product p ON s.product_id = p.id
        INNER JOIN inventory_brand b ON p.brand_id = b.id
        INNER JOIN inventory_category cat ON p.category_id = cat.id
    WHERE 
        (warehouse_name_param IS NULL OR w.name ILIKE '%' || warehouse_name_param || '%')
        AND s.qty >= min_stock
        AND p.is_active = true
    ORDER BY 
        w.name, s.qty DESC, p.name;
END;
$$ LANGUAGE plpgsql;
"""

# Función SQL para obtener el top de productos más vendidos
GET_TOP_SELLING_PRODUCTS_SQL = """
CREATE OR REPLACE FUNCTION get_top_selling_products(
    limit_results INTEGER DEFAULT 10,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    product_id UUID,
    product_name VARCHAR,
    product_sku VARCHAR,
    brand_name VARCHAR,
    category_name VARCHAR,
    total_quantity_sold BIGINT,
    total_orders BIGINT,
    total_revenue DECIMAL,
    avg_unit_price DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id AS product_id,
        p.name AS product_name,
        p.sku AS product_sku,
        b.name AS brand_name,
        c.name AS category_name,
        SUM(oi.qty) AS total_quantity_sold,
        COUNT(DISTINCT o.id) AS total_orders,
        SUM(oi.qty * oi.unit_price) AS total_revenue,
        AVG(oi.unit_price) AS avg_unit_price
    FROM 
        inventory_product p
        INNER JOIN inventory_brand b ON p.brand_id = b.id
        INNER JOIN inventory_category c ON p.category_id = c.id
        INNER JOIN inventory_orderitem oi ON p.id = oi.product_id
        INNER JOIN inventory_order o ON oi.order_id = o.id
    WHERE 
        o.status = 'CONFIRMED'
        AND p.is_active = true
        AND (start_date IS NULL OR o.created_at::DATE >= start_date)
        AND (end_date IS NULL OR o.created_at::DATE <= end_date)
    GROUP BY 
        p.id, p.name, p.sku, b.name, c.name
    ORDER BY 
        total_quantity_sold DESC, total_revenue DESC
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;
"""

# SQL para eliminar las funciones (usado en migración reversa)
DROP_FUNCTIONS_SQL = """
DROP FUNCTION IF EXISTS get_products_by_brand_and_customer(VARCHAR, VARCHAR);
DROP FUNCTION IF EXISTS get_payments_by_product_quantity(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS get_stock_analysis(VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS get_top_selling_products(INTEGER, DATE, DATE);
""" 
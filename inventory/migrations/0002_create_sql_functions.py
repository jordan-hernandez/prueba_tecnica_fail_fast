from django.db import migrations
from inventory.sql_functions import (
    GET_PRODUCTS_BY_BRAND_AND_CUSTOMER_SQL,
    GET_PAYMENTS_BY_PRODUCT_QUANTITY_SQL,
    GET_STOCK_ANALYSIS_SQL,
    GET_TOP_SELLING_PRODUCTS_SQL,
    DROP_FUNCTIONS_SQL
)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=GET_PRODUCTS_BY_BRAND_AND_CUSTOMER_SQL,
            reverse_sql="DROP FUNCTION IF EXISTS get_products_by_brand_and_customer(VARCHAR, VARCHAR);",
        ),
        migrations.RunSQL(
            sql=GET_PAYMENTS_BY_PRODUCT_QUANTITY_SQL,
            reverse_sql="DROP FUNCTION IF EXISTS get_payments_by_product_quantity(VARCHAR, INTEGER);",
        ),
        migrations.RunSQL(
            sql=GET_STOCK_ANALYSIS_SQL,
            reverse_sql="DROP FUNCTION IF EXISTS get_stock_analysis(VARCHAR, INTEGER);",
        ),
        migrations.RunSQL(
            sql=GET_TOP_SELLING_PRODUCTS_SQL,
            reverse_sql="DROP FUNCTION IF EXISTS get_top_selling_products(INTEGER, DATE, DATE);",
        ),
    ]
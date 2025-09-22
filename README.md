# Sistema de Inventario Multi-Bodega

**Prueba Técnica Backend - Django REST Framework + PostgreSQL**

Sistema completo de gestión de inventario multi-bodega con funcionalidades avanzadas de consultas, JOINs parametrizables y comparación de rendimiento entre Django ORM y funciones SQL nativas de PostgreSQL.

## 🎯 Características Principales

- **Inventario Multi-Bodega**: Gestión de stock en múltiples ubicaciones
- **Sistema de Órdenes**: Creación y gestión de órdenes con items múltiples
- **Gestión de Pagos**: Sistema completo de pagos con diferentes métodos
- **API REST Completa**: CRUD para todos los modelos
- **Método get_related Genérico**: JOINs parametrizables y filtros avanzados
- **Funciones SQL PostgreSQL**: Implementación nativa para comparación de rendimiento
- **Datos de Prueba**: Sistema automático de carga de fixtures

## 🧰 Tecnologías

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Base de Datos**: PostgreSQL
- **Lenguaje**: Python 3.8+
- **Arquitectura**: API REST con ViewSets personalizados

## 📦 Estructura del Proyecto

```
prueba_tecnica_backend/
├── inventory_system/           # Configuración principal Django
│   ├── __init__.py
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py               # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── inventory/                 # Aplicación principal
│   ├── models.py             # Modelos de datos (UML implementado)
│   ├── serializers.py        # Serializers DRF
│   ├── views.py              # ViewSets con método get_related
│   ├── admin.py              # Configuración admin Django
│   ├── urls.py               # URLs de la aplicación
│   ├── sql_functions.py      # Funciones SQL PostgreSQL
│   ├── management/
│   │   └── commands/
│   │       ├── load_sample_data.py    # Cargar datos de prueba
│   │       └── compare_sql.py         # Comparar ORM vs SQL
│   └── migrations/
├── manage.py
├── requirements.txt
└── README.md
```

## 🏗️ Modelos Implementados

### Diagrama de Relaciones

El sistema implementa los siguientes modelos según el diagrama UML:

- **Brand**: Marcas de productos
- **Category**: Categorías de productos  
- **Product**: Productos con SKU, precio y relaciones
- **Warehouse**: Bodegas/almacenes
- **Stock**: Stock por producto y bodega (constraint único)
- **Customer**: Clientes del sistema
- **Order**: Órdenes de compra
- **OrderItem**: Items de las órdenes
- **Payment**: Pagos de las órdenes

### Constraints Implementados

```sql
-- Stock único por producto y bodega
CONSTRAINT unique_product_warehouse_stock

-- Stock reservado no puede superar cantidad total
CONSTRAINT reserved_lte_qty

-- Producto único por orden (no duplicados)
CONSTRAINT unique_order_product
```

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes Python)

### 2. Configuración del Entorno

```bash
# Clonar el repositorio
git clone <repository-url>
cd prueba_tecnica_backend

# Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

```sql
-- Crear base de datos PostgreSQL
CREATE DATABASE inventory_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO postgres;
```

**Configuración en `settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Ejecutar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 5. Cargar Datos de Prueba

```bash
# Cargar datos de ejemplo
python manage.py load_sample_data

# O limpiar y cargar datos nuevos
python manage.py load_sample_data --clear
```

### 6. Crear Funciones SQL

```bash
# Ejecutar en PostgreSQL las funciones del archivo sql_functions.py
python manage.py dbshell

# Luego copiar y ejecutar las funciones de inventory/sql_functions.py
```

### 7. Ejecutar Servidor

```bash
python manage.py runserver
```

La API estará disponible en: `http://localhost:8000/api/v1/`

## 📡 Endpoints de la API

### Endpoints Base (CRUD)

| Endpoint | Métodos | Descripción |
|----------|---------|-------------|
| `/api/v1/brands/` | GET, POST, PUT, PATCH, DELETE | Gestión de marcas |
| `/api/v1/categories/` | GET, POST, PUT, PATCH, DELETE | Gestión de categorías |
| `/api/v1/products/` | GET, POST, PUT, PATCH, DELETE | Gestión de productos |
| `/api/v1/warehouses/` | GET, POST, PUT, PATCH, DELETE | Gestión de bodegas |
| `/api/v1/stocks/` | GET, POST, PUT, PATCH, DELETE | Gestión de stock |
| `/api/v1/customers/` | GET, POST, PUT, PATCH, DELETE | Gestión de clientes |
| `/api/v1/orders/` | GET, POST, PUT, PATCH, DELETE | Gestión de órdenes |
| `/api/v1/order-items/` | GET, POST, PUT, PATCH, DELETE | Items de órdenes |
| `/api/v1/payments/` | GET, POST, PUT, PATCH, DELETE | Gestión de pagos |

### Endpoints Especiales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/products/get_related/` | GET | Método genérico con JOINs |
| `/api/v1/products/low_stock/` | GET | Productos con stock bajo |
| `/api/v1/orders/{id}/confirm/` | POST | Confirmar orden y reservar stock |
| `/api/v1/payments/{id}/confirm/` | POST | Confirmar pago |

## 🔗 Método get_related - JOINs Parametrizables

### Funcionalidad Principal

El método `get_related` permite realizar consultas complejas con JOINs parametrizables, filtros anidados y selección de campos específicos.

### Parámetros de Query

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `join` | Relaciones a incluir | `join=brand,category,stocks__warehouse` |
| `fields[modelo]` | Campos específicos por modelo | `fields[product]=name,sku&fields[brand]=name` |
| `filter[modelo]` | Filtros por modelo | `filter[brand]=name__icontains=Samsung` |
| `ordering` | Ordenamiento | `ordering=name,-created_at` |
| `distinct` | Eliminar duplicados | `distinct=true` |
| `limit` | Limitar resultados | `limit=10` |

### Ejemplos de Uso

#### 1. Productos de Samsung ordenados por nombre
```
GET /api/v1/products/get_related/?join=brand,category&filter[brand]=name__icontains=Samsung&ordering=name
```

#### 2. Productos con campos específicos y filtros
```
GET /api/v1/products/get_related/?join=brand,category&fields[product]=name,sku,price&fields[brand]=name&filter[product]=is_active=true
```

#### 3. Productos de una marca en órdenes de un cliente específico
```
GET /api/v1/products/get_related/?join=brand,order_items__order__customer&filter[brand]=name__icontains=Samsung&filter[customer]=email=john@example.com&distinct=true
```

#### 4. Stock por bodega con información completa
```
GET /api/v1/stocks/get_related/?join=product__brand,product__category,warehouse&fields[stock]=qty,reserved&fields[product]=name,sku&fields[warehouse]=name,city
```

### Respuesta del Método get_related

```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid-here",
      "name": "Samsung QLED 55\" 4K Smart TV",
      "sku": "TV-SAMSUNG-001",
      "price": "1299.99",
      "brand": {
        "name": "Samsung"
      },
      "category": {
        "name": "Televisores"
      }
    }
  ],
  "sql_query": "SELECT ... FROM inventory_product ..."
}
```

## 🗄️ Funciones SQL PostgreSQL

### Funciones Implementadas

#### 1. get_products_by_brand_and_customer
Obtiene productos de una marca específica que aparecen en órdenes de un cliente.

```sql
SELECT * FROM get_products_by_brand_and_customer('Samsung', 'john@example.com');
```

#### 2. get_payments_by_product_quantity
Obtiene pagos donde se facturó un producto por más de X unidades.

```sql
SELECT * FROM get_payments_by_product_quantity('TV-SAMSUNG-001', 5);
```

#### 3. get_stock_analysis
Análisis completo de stock por bodega.

```sql
SELECT * FROM get_stock_analysis('Bodega Central', 10);
```

#### 4. get_top_selling_products
Top de productos más vendidos.

```sql
SELECT * FROM get_top_selling_products(10, '2024-01-01', '2024-12-31');
```

## 🔬 Comparación ORM vs SQL

### Ejecutar Comparación

```bash
# Comparar todos los casos
python manage.py compare_sql

# Comparar caso específico
python manage.py compare_sql --case products_by_brand_customer --brand-name Samsung --customer-email john@example.com

# Comparar pagos por cantidad
python manage.py compare_sql --case payments_by_quantity --product-sku TV-SAMSUNG-001 --min-quantity 1
```

### Análisis de Resultados

**Django ORM:**
- ✅ **Ventajas**: Abstracción, seguridad, portabilidad, mantenimiento
- ❌ **Desventajas**: Overhead de conversión, posible problema N+1, mayor uso de memoria

**Funciones PostgreSQL:**
- ✅ **Ventajas**: Velocidad superior, optimización del motor DB, menor uso de memoria
- ❌ **Desventajas**: Acoplamiento a PostgreSQL, mantenimiento manual, menos seguridad

**Complejidad Temporal:**
- **ORM**: O(n) + overhead de Python + múltiples consultas
- **SQL**: O(n) optimizado por motor de base de datos

**Complejidad Espacial:**
- **ORM**: O(n) + objetos Python + cache del ORM
- **SQL**: O(n) solo resultados finales

## 🧪 Casos de Uso de Testing

### Datos Pre-cargados

El comando `load_sample_data` crea:

- **5 Marcas**: Samsung, LG, Sony, Apple, Xiaomi
- **5 Categorías**: Televisores, Smartphones, Laptops, Tablets, Electrodomésticos
- **10 Productos**: Diversos productos de diferentes marcas
- **4 Bodegas**: En Bogotá, Medellín, Cartagena, Cali
- **40 Registros de Stock**: 10 productos × 4 bodegas
- **5 Clientes**: Con emails específicos para testing
- **6 Órdenes**: Con diferentes estados y productos
- **Pagos**: Para órdenes confirmadas

### Casos de Prueba Específicos

1. **Brand + Customer**: Samsung products para john@example.com
2. **Product Quantity**: TV-SAMSUNG-001 con cantidad >= 1
3. **Stock Analysis**: Análisis por bodega "Bodega Central"
4. **Low Stock**: Productos con stock menor a 10 unidades

## 🎮 Ejemplos con cURL

### Crear Producto
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "sku": "TEST-001",
    "price": "99.99",
    "brand": "brand-uuid",
    "category": "category-uuid",
    "is_active": true
  }'
```

### Consulta get_related
```bash
curl "http://localhost:8000/api/v1/products/get_related/?join=brand,category&filter[brand]=name__icontains=Samsung&ordering=name"
```

### Confirmar Orden
```bash
curl -X POST http://localhost:8000/api/v1/orders/order-uuid/confirm/
```

## 📊 Colección Postman

### Requests Incluidos

1. **CRUD Completo de Products**
   - GET /products/ (List)
   - POST /products/ (Create) 
   - GET /products/{id}/ (Detail)
   - PUT /products/{id}/ (Update)
   - DELETE /products/{id}/ (Delete)

2. **Método get_related Examples**
   - Products with Brand and Category
   - Products by Brand Samsung
   - Products in Customer Orders
   - Stock Analysis with Joins
   - Custom Fields Selection

3. **Business Logic**
   - Low Stock Products
   - Confirm Order
   - Confirm Payment
   - Customer Orders

4. **SQL Functions Testing**
   - Test equivalent queries

### Variables de Entorno Postman

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "samsung_brand_id": "{{brand_id}}",
  "test_customer_email": "john@example.com",
  "test_product_sku": "TV-SAMSUNG-001"
}
```

## 🐛 Debugging y Desarrollo

### Ver SQL Generado

```python
# En Django shell
from inventory.models import Product
qs = Product.objects.select_related('brand').filter(brand__name='Samsung')
print(str(qs.query))
```

### Logs de SQL

El proyecto está configurado para mostrar todas las consultas SQL en modo DEBUG:

```python
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

### Testing

```bash
# Ejecutar tests
python manage.py test

# Test específico
python manage.py test inventory.tests.test_models

# Con coverage
coverage run manage.py test
coverage html
```

## 🔧 Configuración Adicional

### Variables de Entorno (.env)

```bash
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Configuración para Producción

```python
# settings.py para producción
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Base de datos con connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'OPTIONS': {
                'MAX_CONNS': 20,
            }
        }
    }
}
```

## 📈 Métricas de Rendimiento

### Benchmarks Esperados

- **ORM Queries**: ~50-100ms para consultas complejas
- **SQL Functions**: ~10-30ms para las mismas consultas
- **Memory Usage**: SQL functions usan ~60% menos memoria
- **Scalability**: SQL functions escalan mejor con grandes datasets

### Optimizaciones Implementadas

1. **Índices de Base de Datos**: En campos frecuentemente consultados
2. **select_related / prefetch_related**: Para evitar N+1 queries
3. **Constraints a Nivel DB**: Para integridad de datos
4. **Conexión Pooling**: Para mejor rendimiento
5. **Query Optimization**: Análisis de planes de ejecución

## 🤝 Contribución

### Extensiones Posibles

1. **Cache**: Implementar Redis para cacheo de consultas frecuentes
2. **Elasticsearch**: Para búsquedas de texto completo
3. **GraphQL**: API alternativa con Apollo Server
4. **Docker**: Containerización completa
5. **CI/CD**: Pipeline de integración continua
6. **Monitoring**: APM con New Relic o DataDog

### Estructura de Contribución

```bash
# Fork del repositorio
git clone your-fork-url
cd prueba_tecnica_backend

# Crear rama feature
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commit
git commit -m "Add: nueva funcionalidad"

# Push y crear PR
git push origin feature/nueva-funcionalidad
```

## 📝 Licencia

Este proyecto es parte de una prueba técnica y está disponible bajo licencia MIT.

---

**Desarrollado como parte de la prueba técnica Backend - Django REST Framework + PostgreSQL**

Para dudas o consultas sobre la implementación, revisar la documentación de código o contactar al desarrollador. 
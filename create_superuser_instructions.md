# Configuración de Superusuario Django Admin

## 🎯 Credenciales para el Video de Demostración

### Crear Superusuario
```bash
# 1. Activar entorno virtual
.\venv\Scripts\Activate

# 2. Crear superusuario
python manage.py createsuperuser

# 3. Usar estas credenciales:
Username: admin
Email: admin@admin.com  
Password: admin123
```

### Acceso al Admin
```
URL: http://127.0.0.1:8000/admin/
Usuario: admin
Contraseña: admin123
```

## 🔧 Script Automático (Opcional)

Si quieres crear el superusuario automáticamente, puedes usar:

```python
# En Django shell: python manage.py shell
from django.contrib.auth.models import User

# Crear superusuario automáticamente
User.objects.create_superuser(
    username='admin',
    email='admin@admin.com',
    password='admin123'
)
```

## 📊 Qué Verás en el Admin

Una vez logueado, podrás administrar:
- ✅ **Brands** (Marcas)
- ✅ **Categories** (Categorías) 
- ✅ **Products** (Productos)
- ✅ **Warehouses** (Bodegas)
- ✅ **Stock** (Stock por producto/bodega)
- ✅ **Customers** (Clientes)
- ✅ **Orders** (Órdenes)
- ✅ **Order Items** (Items de órdenes)
- ✅ **Payments** (Pagos)

## 🎥 Para el Video

Perfecto para demostrar:
1. **Interface de administración** completa
2. **Relaciones entre modelos** en el admin
3. **Validaciones y constraints** 
4. **Datos de prueba** cargados
5. **Funcionalidad CRUD** desde interfaz web 
# ✅ ERROR SOLUCIONADO: "Object of type datetime is not JSON serializable"

## 🚨 **Problema Original**
n8n reportaba el error:
```
"Object of type datetime is not JSON serializable"
```

Al hacer peticiones POST a los endpoints del servidor MCP Odoo.

## 🔧 **Causa del Problema**
Los objetos `datetime` que Odoo devuelve en campos como `create_date` y `write_date` no pueden ser serializados directamente a JSON por Python.

## ✅ **Solución Implementada**

### **1. Función de Serialización**
```python
def serialize_datetime_objects(obj):
    """Convierte recursivamente objetos datetime en strings para serialización JSON"""
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, dict):
        return {key: serialize_datetime_objects(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_objects(item) for item in obj]
    else:
        return obj
```

### **2. Aplicada a todas las funciones que devuelven datos de Odoo**
- ✅ `get_leads()` - Obtener leads del CRM
- ✅ `get_partners()` - Obtener partners/clientes  
- ✅ `create_lead()` - Crear nuevos leads
- ✅ `create_partner()` - Crear nuevos partners
- ✅ `update_lead()` - Actualizar leads existentes
- ✅ `update_partner()` - Actualizar partners existentes
- ✅ `get_crm_stages()` - Obtener etapas del CRM
- ✅ `get_crm_teams()` - Obtener equipos de ventas
- ✅ `get_countries()` - Obtener países
- ✅ `test_connection()` - Probar conexión

## 🎯 **Cómo usar n8n ahora**

### **URL del Servidor**
```
https://dev2.odoo.universidadisep.com
```

### **Puerto Configurado**
```
8001 (para Coolify)
```

### **Ejemplo de Request en n8n que ahora funcionará**

**Node**: HTTP Request  
**Método**: POST  
**URL**: `https://dev2.odoo.universidadisep.com/mcp/get_leads`  
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```
**Body**:
```json
{
  "limit": 10
}
```

### **Respuesta Esperada (AHORA SIN ERRORES)**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "Lead Example",
      "create_date": "2025-08-13 08:30:27",  ← ¡YA ES STRING!
      "write_date": "2025-08-13 08:30:27",   ← ¡YA ES STRING!
      "email_from": "cliente@ejemplo.com",
      "partner_name": "Empresa Cliente"
    }
  ],
  "count": 1,
  "message": "Se encontraron 1 leads de 1 total"
}
```

## 🔄 **Deployment en Coolify**

El servidor está configurado para ejecutarse en puerto **8001** para evitar conflictos en Coolify:

```yaml
# docker-compose.yml
ports:
  - "8001:8001"
environment:
  - PORT=8001
```

## 🧪 **Testing**

Puedes probar que funciona:

### **1. Health Check**
```bash
GET https://dev2.odoo.universidadisep.com/health
```

### **2. Obtener Leads (el que estaba fallando)**
```bash
POST https://dev2.odoo.universidadisep.com/mcp/get_leads
Content-Type: application/json

{
  "limit": 5
}
```

## 📚 **Archivos Actualizados**

- ✅ `odoo_client.py` - Agregada función de serialización datetime
- ✅ `main.py` - Sin cambios (sigue siendo HTTP server)
- ✅ `docker-compose.yml` - Puerto 8001 configurado
- ✅ `.env` - PORT=8001

## 🎉 **Resultado**

**ANTES** (con error):
```json
{
  "error": "Object of type datetime is not JSON serializable"
}
```

**AHORA** (funcionando):
```json
{
  "success": true,
  "data": [...],
  "message": "Se encontraron X leads"
}
```

---

🚀 **¡El error está completamente solucionado! Ahora puedes usar todos los endpoints en n8n sin problemas de serialización datetime.**

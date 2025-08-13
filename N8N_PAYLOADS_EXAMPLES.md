# 📋 Ejemplos de Payloads para n8n - Servidor MCP Odoo

## 🔗 URL Base
```
https://dev2.odoo.universidadisep.com
```

## 📊 1. Obtener Leads - `/mcp/get_leads`

### **Payload Básico**:
```json
{
  "limit": 10
}
```

### **Payload con Filtros**:
```json
{
  "stage_id": 1,
  "user_id": 2,
  "partner_id": null,
  "limit": 20
}
```

### **Payload para Leads Nuevos**:
```json
{
  "stage_id": 1,
  "limit": 5
}
```

### **Respuesta Esperada**:
```json
{
  "success": true,
  "results": [
    {
      "id": 123,
      "name": "Lead Example",
      "email": "lead@example.com",
      "phone": "+34 600 123 456",
      "partner_name": "Company Name",
      "stage": "Nuevo",
      "user": "Sales User",
      "create_date": "2025-08-13",
      "probability": 10.0,
      "expected_revenue": 1000.0
    }
  ],
  "count": 1
}
```

## 🆕 2. Crear Lead - `/mcp/create_lead`

### **Payload Mínimo**:
```json
{
  "name": "Lead desde n8n"
}
```

### **Payload Completo**:
```json
{
  "name": "Oportunidad Importante",
  "email": "cliente@empresa.com",
  "phone": "+34 91 123 4567",
  "mobile": "+34 600 987 654",
  "partner_name": "Empresa Cliente SL",
  "website": "https://empresacliente.com",
  "street": "Calle Principal 123",
  "city": "Madrid",
  "zip": "28001",
  "country_id": 68,
  "description": "Lead creado automáticamente desde n8n con información completa",
  "type": "opportunity",
  "priority": "2",
  "expected_revenue": 5000.0,
  "probability": 25.0,
  "user_id": 2,
  "tag_ids": [1, 2, 3]
}
```

### **Payload para Lead B2B**:
```json
{
  "name": "Consulta Servicios IT",
  "email": "contacto@techcorp.com", 
  "phone": "+34 93 456 7890",
  "partner_name": "TechCorp Solutions",
  "website": "https://techcorp.com",
  "description": "Interesados en servicios de desarrollo web y aplicaciones móviles",
  "type": "lead",
  "priority": "1",
  "tag_ids": [5, 8]
}
```

### **Respuesta Esperada**:
```json
{
  "success": true,
  "lead_id": 456,
  "message": "Lead creado exitosamente",
  "lead_data": {
    "id": 456,
    "name": "Oportunidad Importante",
    "email": "cliente@empresa.com",
    "stage": "Nuevo",
    "create_date": "2025-08-13"
  }
}
```

## 👥 3. Obtener Partners - `/mcp/get_partners`

### **Payload para Empresas**:
```json
{
  "is_company": true,
  "limit": 15
}
```

### **Payload para Personas**:
```json
{
  "is_company": false,
  "limit": 10
}
```

### **Payload con Filtro por País**:
```json
{
  "is_company": true,
  "country_id": 68,
  "limit": 20
}
```

### **Respuesta Esperada**:
```json
{
  "success": true,
  "results": [
    {
      "id": 789,
      "name": "Partner Company",
      "email": "info@partner.com",
      "phone": "+34 91 555 0123",
      "is_company": true,
      "website": "https://partner.com",
      "street": "Avenida Ejemplo 456",
      "city": "Barcelona",
      "country": "España"
    }
  ],
  "count": 1
}
```

## 🆕 4. Crear Partner - `/mcp/create_partner`

### **Payload para Empresa**:
```json
{
  "name": "Innovate Tech SL",
  "email": "contacto@innovatetech.com",
  "phone": "+34 91 987 6543",
  "mobile": "+34 600 111 222",
  "is_company": true,
  "website": "https://innovatetech.com",
  "street": "Calle Tecnología 789",
  "street2": "Edificio A, Planta 3",
  "city": "Madrid",
  "zip": "28020",
  "country_id": 68,
  "vat": "ESB12345678",
  "category_id": [1, 3]
}
```

### **Payload para Persona**:
```json
{
  "name": "Juan García López",
  "email": "juan.garcia@email.com",
  "phone": "+34 93 123 4567",
  "mobile": "+34 666 777 888",
  "is_company": false,
  "street": "Calle Menor 12",
  "city": "Valencia",
  "zip": "46001",
  "country_id": 68
}
```

### **Respuesta Esperada**:
```json
{
  "success": true,
  "partner_id": 234,
  "message": "Partner creado exitosamente",
  "partner_data": {
    "id": 234,
    "name": "Innovate Tech SL",
    "email": "contacto@innovatetech.com",
    "is_company": true
  }
}
```

## 🤖 5. Consulta Natural - `/mcp/natural_query`

### **Análisis de Leads**:
```json
{
  "query": "¿Cuántos leads nuevos tengo esta semana?",
  "context": "weekly leads analysis"
}
```

### **Búsqueda de Partners**:
```json
{
  "query": "Muéstrame las empresas de tecnología en Madrid",
  "context": "tech companies madrid"
}
```

### **Creación Inteligente**:
```json
{
  "query": "Crear un lead para una consultoría de marketing digital en Barcelona",
  "context": "lead creation marketing consultancy"
}
```

### **Análisis de Ventas**:
```json
{
  "query": "¿Cuáles son mis oportunidades más prometedoras este mes?",
  "context": "sales opportunities analysis"
}
```

### **Respuesta Esperada**:
```json
{
  "success": true,
  "response": "He encontrado 5 leads nuevos esta semana: 3 en etapa 'Nuevo' y 2 en 'Calificado'. El total de revenue esperado es de €15,000.",
  "data": {
    "leads_count": 5,
    "new_stage": 3,
    "qualified_stage": 2,
    "expected_revenue": 15000
  },
  "anthropic_used": true
}
```

## 🔍 6. Health Check - `/health`

### **Request**:
```
GET /health
```

### **Respuesta Esperada**:
```json
{
  "status": "healthy",
  "service": "odoo-mcp-server",
  "version": "1.0.0",
  "odoo_connected": true,
  "anthropic_available": true,
  "timestamp": "1692123456.789"
}
```

## 📝 7. Info del Servidor - `/`

### **Request**:
```
GET /
```

### **Respuesta Esperada**:
```json
{
  "message": "Odoo MCP Server",
  "status": "running", 
  "health_endpoint": "/health",
  "mcp_tools": [
    "get_leads",
    "create_lead", 
    "update_lead",
    "get_partners",
    "create_partner",
    "natural_language_query"
  ]
}
```

## 🚨 Respuestas de Error

### **Error de Validación**:
```json
{
  "error": "Campo 'name' es requerido para crear lead",
  "status_code": 400
}
```

### **Error de Conexión Odoo**:
```json
{
  "error": "No se pudo conectar a Odoo. Verificar configuración.",
  "status_code": 503
}
```

### **Error de Anthropic**:
```json
{
  "error": "Servicio Anthropic no disponible. Usando respuesta básica.",
  "status_code": 502
}
```

## 💡 Tips para n8n

### **Headers Requeridos**:
```json
{
  "Content-Type": "application/json"
}
```

### **Configuración HTTP Request Node**:
- **Method**: POST (para endpoints MCP)
- **URL**: `https://dev2.odoo.universidadisep.com/mcp/ENDPOINT`
- **Body Type**: JSON
- **Timeout**: 30000ms
- **Retry on Fail**: 3 attempts

### **Validación en Function Node**:
```javascript
// Verificar respuesta exitosa
if (items[0].json.error) {
  throw new Error(`API Error: ${items[0].json.error}`);
}

// Procesar datos exitosos
const data = items[0].json.results || items[0].json.data;
return [{ json: { processedData: data } }];
```

---

🎯 **¡Con estos ejemplos puedes implementar cualquier flujo de trabajo en n8n!**

Copia y pega estos payloads directamente en tus HTTP Request nodes.

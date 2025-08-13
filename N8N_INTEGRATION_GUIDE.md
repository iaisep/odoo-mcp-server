# 🚀 Guía de Integración n8n - Servidor MCP Odoo

## 📋 Configuración Inicial en n8n

### 🔗 URL Base del Servidor
```
https://dev2.odoo.universidadisep.com
```

## 🛠️ Endpoints Disponibles

### 1. **Health Check** 
- **Método**: `GET`
- **URL**: `/health`
- **Uso**: Verificar que el servidor está funcionando

### 2. **Información del Servidor**
- **Método**: `GET` 
- **URL**: `/`
- **Uso**: Ver endpoints disponibles y estado

### 3. **Obtener Leads**
- **Método**: `POST`
- **URL**: `/mcp/get_leads`
- **Headers**: `Content-Type: application/json`

### 4. **Crear Lead**
- **Método**: `POST`
- **URL**: `/mcp/create_lead` 
- **Headers**: `Content-Type: application/json`

### 5. **Obtener Partners**
- **Método**: `POST`
- **URL**: `/mcp/get_partners`
- **Headers**: `Content-Type: application/json`

### 6. **Crear Partner**
- **Método**: `POST`
- **URL**: `/mcp/create_partner`
- **Headers**: `Content-Type: application/json`

### 7. **Consulta en Lenguaje Natural**
- **Método**: `POST`
- **URL**: `/mcp/natural_query`
- **Headers**: `Content-Type: application/json`

## 📖 Ejemplos de Uso en n8n

### 🔍 **1. Health Check**

**Node**: HTTP Request
```json
{
  "method": "GET",
  "url": "https://dev2.odoo.universidadisep.com/health"
}
```

**Respuesta esperada**:
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

### 📊 **2. Obtener Leads**

**Node**: HTTP Request
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/get_leads",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "limit": 10,
    "stage_id": null,
    "user_id": null,
    "partner_id": null
  }
}
```

**Filtros disponibles**:
```json
{
  "stage_id": 1,        // ID de etapa específica
  "user_id": 2,         // ID de usuario asignado
  "partner_id": 5,      // ID de partner/cliente
  "limit": 20           // Límite de resultados (default: 10)
}
```

### 🆕 **3. Crear Lead**

**Node**: HTTP Request
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/create_lead",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "Lead desde n8n",
    "email": "cliente@ejemplo.com",
    "phone": "+34 600 123 456",
    "partner_name": "Empresa Cliente",
    "description": "Lead creado automáticamente desde n8n",
    "type": "lead"
  }
}
```

**Campos disponibles**:
```json
{
  "name": "Nombre del lead (requerido)",
  "email": "email@cliente.com",
  "phone": "+34 600 000 000", 
  "mobile": "+34 700 000 000",
  "partner_name": "Nombre de la empresa",
  "website": "https://cliente.com",
  "description": "Descripción del lead",
  "type": "lead",  // o "opportunity"
  "priority": "1", // 0=Baja, 1=Normal, 2=Alta, 3=Muy Alta
  "stage_id": 1,   // ID de etapa específica
  "user_id": 2,    // ID del usuario asignado
  "tag_ids": [1, 2, 3] // IDs de etiquetas
}
```

### 👥 **4. Obtener Partners**

**Node**: HTTP Request  
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/get_partners",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "is_company": true,
    "limit": 15
  }
}
```

**Filtros disponibles**:
```json
{
  "is_company": true,      // true=empresas, false=personas
  "country_id": 68,        // ID del país (68=España)
  "category_ids": [1, 2],  // IDs de categorías
  "limit": 25              // Límite de resultados
}
```

### 🆕 **5. Crear Partner**

**Node**: HTTP Request
```json
{
  "method": "POST", 
  "url": "https://dev2.odoo.universidadisep.com/mcp/create_partner",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "Nueva Empresa SL",
    "email": "contacto@nuevaempresa.com",
    "phone": "+34 91 123 4567",
    "is_company": true,
    "website": "https://nuevaempresa.com",
    "street": "Calle Principal 123",
    "city": "Madrid",
    "zip": "28001"
  }
}
```

### 🤖 **6. Consulta en Lenguaje Natural**

**Node**: HTTP Request
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/natural_query", 
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "query": "¿Cuántos leads tengo pendientes este mes?",
    "context": "CRM leads analysis"
  }
}
```

**Ejemplos de consultas**:
```json
{
  "query": "Muéstrame los leads más importantes",
  "context": "priority leads"
}

{
  "query": "¿Qué partners son empresas en España?", 
  "context": "spanish companies"
}

{
  "query": "Crear un lead para una empresa de tecnología",
  "context": "lead creation tech company"
}
```

## 🔄 Workflow Típico en n8n

### **Ejemplo 1: Procesar Leads Nuevos**

1. **Trigger**: Webhook o Schedule
2. **HTTP Request**: Obtener leads nuevos
   ```json
   POST /mcp/get_leads
   {"limit": 5, "stage_id": 1}
   ```
3. **Function**: Procesar datos de leads
4. **Condition**: Verificar criterios
5. **HTTP Request**: Crear tareas o notificaciones

### **Ejemplo 2: Sincronización con CRM Externo**

1. **HTTP Request**: Obtener datos de CRM externo
2. **Function**: Transformar datos al formato Odoo
3. **HTTP Request**: Crear lead en Odoo
   ```json
   POST /mcp/create_lead
   {datos_transformados}
   ```
4. **HTTP Request**: Confirmar sincronización

### **Ejemplo 3: Análisis Inteligente**

1. **Schedule Trigger**: Ejecutar diariamente
2. **HTTP Request**: Consulta natural para análisis
   ```json
   POST /mcp/natural_query
   {"query": "Resumen de leads de hoy", "context": "daily report"}
   ```
3. **Email/Slack**: Enviar reporte automático

## 🛡️ Manejo de Errores

### **Respuesta de Error Típica**:
```json
{
  "error": "Descripción del error",
  "status_code": 500
}
```

### **En n8n - Node Error Handling**:
```javascript
// En Function Node
if (items[0].json.error) {
  throw new Error(`API Error: ${items[0].json.error}`);
}

// Continuar procesamiento normal
return items;
```

## 🔐 Autenticación

**Actualmente**: No se requiere autenticación (servidor interno)
**Para producción**: Considerar agregar API keys o JWT tokens

## 📊 Monitoring en n8n

### **Health Check Workflow**:
1. **Schedule**: Cada 5 minutos
2. **HTTP Request**: `GET /health`
3. **Condition**: Verificar status="healthy"
4. **Alert**: Notificar si falla

## 💡 Tips y Mejores Prácticas

### **1. Timeouts**
- Configurar timeout de 30 segundos en HTTP Request nodes
- Las consultas con Anthropic pueden tardar más

### **2. Retry Logic**
- Habilitar retry en HTTP Request nodes
- 3 reintentos con 5 segundos de pausa

### **3. Rate Limiting**
- No hacer más de 10 requests/segundo
- Usar Wait nodes entre llamadas masivas

### **4. Error Handling**
- Siempre verificar response status
- Implementar fallbacks para servicios críticos

### **5. Data Validation**
```javascript
// Validar respuesta en Function Node
const data = items[0].json;
if (!data.success && !data.results) {
  throw new Error('Invalid response format');
}
```

## 📱 Ejemplo Completo de Workflow

```json
{
  "name": "Odoo MCP - Sync Leads",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "hour": "*",
          "minute": "*/15"
        }
      }
    },
    {
      "name": "Get New Leads", 
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://dev2.odoo.universidadisep.com/mcp/get_leads",
        "jsonParameters": true,
        "options": {
          "timeout": 30000
        },
        "bodyParametersJson": {
          "limit": 10,
          "stage_id": 1
        }
      }
    },
    {
      "name": "Process Leads",
      "type": "n8n-nodes-base.function", 
      "parameters": {
        "functionCode": "// Procesar leads y preparar para CRM externo\\nreturn items;"
      }
    }
  ]
}
```

---

🎯 **¡Con esta guía puedes integrar completamente el servidor MCP Odoo con n8n!**

¿Necesitas ayuda con algún endpoint específico o workflow en particular?

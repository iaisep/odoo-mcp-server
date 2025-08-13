# 🚨 Solución de Errores n8n - Servidor MCP Odoo

## ❌ Errores Más Comunes y Soluciones

### 1. **Error de Conexión - "ECONNREFUSED"**

**Error típico**:
```
Error: connect ECONNREFUSED 
RequestError: Error: connect ECONNREFUSED
```

**Causas posibles**:
- El servidor no está ejecutándose
- URL incorrecta
- Puerto bloqueado

**Soluciones**:

#### ✅ Verificar el servidor:
```bash
# Probar health check
curl https://dev2.odoo.universidadisep.com/health
```

#### ✅ Configuración correcta en n8n:
```json
{
  "method": "GET",
  "url": "https://dev2.odoo.universidadisep.com/health",
  "options": {
    "timeout": 30000,
    "followRedirect": true
  }
}
```

### 2. **Error 503 - "Service Unavailable"**

**Error típico**:
```
HTTP 503: Service Unavailable
no available server
```

**Causa**: Servidor en Coolify reiniciándose o no saludable

**Soluciones**:
1. Verificar estado en Coolify dashboard
2. Revisar logs del contenedor
3. Trigger manual redeploy

### 3. **Error 500 - "Internal Server Error"**

**Error típico**:
```
HTTP 500: Internal Server Error
{"error": "Error description"}
```

**Causas comunes**:
- Datos mal formateados en el body
- Campos requeridos faltantes
- Error en conexión a Odoo

**Soluciones**:

#### ✅ Validar JSON en n8n:
```javascript
// Function Node - Validar antes de enviar
const payload = {
  name: $('previous_node').item.json.name || 'Sin nombre',
  email: $('previous_node').item.json.email || null
};

// Validar campos requeridos
if (!payload.name) {
  throw new Error('Campo name es requerido');
}

return [{ json: payload }];
```

### 4. **Error de Timeout**

**Error típico**:
```
Error: Request timeout
ETIMEDOUT
```

**Solución**:
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/natural_query",
  "options": {
    "timeout": 60000,
    "retry": {
      "limit": 3,
      "delay": 5000
    }
  }
}
```

### 5. **Error de Formato JSON**

**Error típico**:
```
SyntaxError: Unexpected token in JSON
Invalid JSON response
```

**Causa**: Respuesta no es JSON válido

**Solución en n8n**:
```javascript
// Function Node - Procesar respuesta
try {
  const response = items[0].json;
  
  // Si la respuesta es string, intentar parsear
  if (typeof response === 'string') {
    const parsed = JSON.parse(response);
    return [{ json: parsed }];
  }
  
  return items;
} catch (error) {
  throw new Error(`Error parsing JSON: ${error.message}`);
}
```

### 6. **Error SSL/TLS**

**Error típico**:
```
Error: unable to verify the first certificate
CERT_UNTRUSTED
```

**Solución**:
```json
{
  "method": "POST",
  "url": "https://dev2.odoo.universidadisep.com/mcp/get_leads",
  "options": {
    "skipSslCertificateValidation": true
  }
}
```

## 🔧 Workflow de Debugging en n8n

### **1. Test Health Check**
```json
{
  "name": "Test Health",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://dev2.odoo.universidadisep.com/health",
    "options": {
      "timeout": 10000
    }
  }
}
```

### **2. Test Simple Endpoint**
```json
{
  "name": "Test Get Leads",
  "type": "n8n-nodes-base.httpRequest", 
  "parameters": {
    "method": "POST",
    "url": "https://dev2.odoo.universidadisep.com/mcp/get_leads",
    "jsonParameters": true,
    "bodyParametersJson": {
      "limit": 1
    },
    "options": {
      "timeout": 30000
    }
  }
}
```

### **3. Error Handler Function**
```javascript
// Function Node para manejar errores
const items = $input.all();

return items.map(item => {
  try {
    // Verificar si hay error en la respuesta
    if (item.json.error) {
      return {
        json: {
          success: false,
          error: item.json.error,
          original_data: item.json
        }
      };
    }
    
    // Si hay datos válidos
    if (item.json.results) {
      return {
        json: {
          success: true,
          count: item.json.results.length,
          data: item.json.results
        }
      };
    }
    
    // Caso por defecto
    return {
      json: {
        success: true,
        data: item.json
      }
    };
    
  } catch (error) {
    return {
      json: {
        success: false,
        error: error.message,
        original_item: item
      }
    };
  }
});
```

## 🚨 Casos Específicos de Error

### **Error: "get_leads function undefined"**
**Causa**: Función no existe en el servidor
**Solución**: Verificar que el endpoint sea `/mcp/get_leads` no `get_leads`

### **Error: "Odoo connection failed"**
**Causa**: Servidor no puede conectar a Odoo
**Solución**: Verificar credentials en variables de entorno de Coolify

### **Error: "Anthropic API key invalid"**  
**Causa**: API key de Anthropic inválida
**Solución**: Las consultas naturales fallarán, pero otros endpoints funcionarán

## 📋 Checklist de Debugging

### ✅ **Antes de reportar error**:

1. **¿El health check funciona?**
   ```bash
   curl https://dev2.odoo.universidadisep.com/health
   ```

2. **¿La URL es correcta?**
   - ✅ `https://dev2.odoo.universidadisep.com/mcp/get_leads`
   - ❌ `https://dev2.odoo.universidadisep.com/get_leads`

3. **¿El Content-Type está configurado?**
   ```json
   "headers": {
     "Content-Type": "application/json"
   }
   ```

4. **¿El JSON está bien formateado?**
   ```json
   {
     "limit": 10,
     "stage_id": null
   }
   ```

5. **¿El timeout es suficiente?**
   ```json
   "options": {
     "timeout": 30000
   }
   ```

## 🛠️ Plantilla de Workflow para Testing

```json
{
  "name": "MCP Server Debug",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger"
    },
    {
      "name": "Test Health",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET", 
        "url": "https://dev2.odoo.universidadisep.com/health"
      }
    },
    {
      "name": "Check Response",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "console.log('Health Response:', JSON.stringify(items[0].json, null, 2)); return items;"
      }
    },
    {
      "name": "Test Leads",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://dev2.odoo.universidadisep.com/mcp/get_leads",
        "jsonParameters": true,
        "bodyParametersJson": {"limit": 1}
      }
    },
    {
      "name": "Log Results", 
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "console.log('Leads Response:', JSON.stringify(items[0].json, null, 2)); return items;"
      }
    }
  ]
}
```

---

## 📞 **¿Qué error específico estás viendo?**

Por favor compárteme:
1. **El mensaje de error exacto**
2. **Qué endpoint estás llamando**
3. **El payload que estás enviando**
4. **Configuración del HTTP Request node**

¡Así podremos solucionarlo rápidamente! 🚀

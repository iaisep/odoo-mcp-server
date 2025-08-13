# 🚑 Guía de Solución para Coolify "503 - no available server"

## 🔍 Problema Identificado
Tu URL de Coolify: `https://dev2.odoo.universidadisep.com/`
Error: **503 - no available server**

## ✅ Lo que está funcionando:
- ✅ Odoo connection working
- ✅ Anthropic client working  
- ✅ Coolify platform responding (no network issues)

## ❌ Lo que necesita arreglo:
- ❌ Application container not running/healthy in Coolify

## 🔧 Pasos para solucionar:

### 1. Acceder al Dashboard de Coolify
Ve a: `https://dev2.odoo.universidadisep.com:8000` (puerto admin)
O el dashboard principal de tu Coolify

### 2. Revisar el estado de la aplicación
- Busca tu aplicación `odoo-mcp-server`
- Revisa si está "Running" o "Failed"
- Mira los logs de deployment

### 3. Trigger nuevo deployment
Con los fixes que acabamos de hacer:
```bash
# Los fixes están ya en GitHub:
- Fix FastMCP.__init__() version parameter ✅
- Fix FastMCP.run() host/port parameters ✅
```

### 4. Variables de entorno requeridas
Asegúrate que estas variables estén configuradas en Coolify:

```env
# ESENCIALES (REQUERIDAS)
ODOO_URL=https://sunafront.universidadisep.com
ODOO_DB=UniversidadISep
ODOO_USERNAME=iallamadas@universidadisep.com
ODOO_PASSWORD=Veronica023_

# OPCIONALES
ANTHROPIC_API_KEY=tu_key_si_la_tienes
PORT=8083
HOST=0.0.0.0
LOG_LEVEL=INFO
```

### 5. Comandos útiles para debugging en Coolify:

#### Ver logs de la aplicación:
```bash
# En el dashboard de Coolify o SSH
docker logs <container_name> --tail 50
```

#### Rebuild y redeploy:
- Trigger manual deployment
- O push dummy commit para auto-deploy

### 6. Health check URL para verificar:
Una vez que funcione, deberías poder acceder a:
```
https://dev2.odoo.universidadisep.com/health
```

Y ver algo como:
```json
{
  "status": "healthy",
  "service": "odoo-mcp-server",
  "odoo_connected": true,
  "anthropic_available": true,
  "timestamp": "..."
}
```

## 🎯 Acción inmediata recomendada:

1. **Ve al dashboard de Coolify**
2. **Encuentra tu app odoo-mcp-server**
3. **Trigger nuevo deployment** (los fixes están listos)
4. **Monitorea los logs** durante el deployment
5. **Prueba el health check** cuando complete

¡Los errores de FastMCP ya están corregidos en GitHub, solo necesitas un nuevo deployment! 🚀

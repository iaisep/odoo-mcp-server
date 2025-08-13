# 🚀 Guía Completa de Deployment en Coolify

## ✅ Estado Actual del Proyecto

- ✅ Servidor MCP completo implementado
- ✅ Conexión a Odoo funcionando (sunafront.universidadisep.com)
- ✅ Repositorio GitHub creado: https://github.com/iaisep/odoo-mcp-server
- ✅ Configuración Docker lista para producción
- 🔄 **LISTO PARA DEPLOY EN COOLIFY**

## 📁 Archivos de Deployment Creados

```
📦 odoo-mcp-server/
├── 🐳 Dockerfile              # Configuración del contenedor
├── 🐳 docker-compose.yml     # Para testing local
├── ⚙️ coolify.conf            # Configuración específica de Coolify  
├── 📋 DEPLOYMENT.md           # Guía detallada de deployment
├── 🔧 build-and-test.sh       # Script de testing (Linux/Mac)
├── 🔧 build-and-test.ps1      # Script de testing (Windows)
└── 📚 README.md               # Documentación principal
```

## 🚀 Pasos para Deploy en Coolify

### 1. Acceder a Coolify Dashboard
- Ve a tu instancia de Coolify
- Login con tus credenciales

### 2. Crear Nueva Aplicación
1. **New Resource** → **Application**
2. **Public Repository** → GitHub
3. **Repository URL**: `https://github.com/iaisep/odoo-mcp-server`
4. **Branch**: `main`
5. **Build Pack**: `Docker`

### 3. Configurar Variables de Entorno

#### 🔑 Variables Esenciales (REQUERIDAS):
```env
ODOO_URL=https://sunafront.universidadisep.com
ODOO_DB=UniversidadISep  
ODOO_USERNAME=iallamadas@universidadisep.com
ODOO_PASSWORD=Veronica023_
PORT=8083
HOST=0.0.0.0
```

#### 🤖 Variables de IA (OPCIONALES):
```env
ANTHROPIC_API_KEY=tu_api_key_aquí
OPENAI_API_KEY=tu_api_key_aquí
```

#### ⚙️ Variables de Configuración:
```env
LOG_LEVEL=INFO
DEV_MODE=false
MOCK_ODOO_DATA=false
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0
```

### 4. Configurar Red y Dominio
- **Puerto**: `8083`
- **Health Check**: `/health`
- **Dominio**: Asignar subdominio (ej: `odoo-mcp.tudominio.com`)
- **SSL**: Habilitar automático

### 5. Iniciar Deployment
1. **Deploy** → Confirmar
2. **Monitor Logs** en tiempo real
3. **Verificar** cuando complete

## ✅ Verificación Post-Deploy

### Health Check
```bash
curl https://tu-dominio.com/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "odoo-mcp-server", 
  "version": "1.0.0",
  "odoo_connected": true,
  "anthropic_available": false,
  "timestamp": "1692123456.789"
}
```

## 🛠️ Herramientas MCP Disponibles

Una vez deployado, el servidor expondrá estas 6 herramientas MCP:

1. **`get_leads`** - Obtener leads de CRM
2. **`create_lead`** - Crear nuevo lead
3. **`update_lead`** - Actualizar lead existente
4. **`get_partners`** - Obtener partners/contactos
5. **`create_partner`** - Crear nuevo partner
6. **`natural_language_query`** - Consultas en lenguaje natural

## 🔗 Integración con n8n

### Endpoint del servidor:
```
https://tu-dominio.com
```

### Configuración en n8n:
1. Usar HTTP Request node apuntando al endpoint
2. O configurar MCP client nativo si está disponible
3. Acceso a todas las herramientas via JSON-RPC

## 📊 Monitoreo

### Logs
- Dashboard de Coolify → Application → Logs
- Logs en tiempo real disponibles

### Métricas
- CPU, Memoria, Red en dashboard
- Health checks automáticos cada 30s

## 🎯 Siguiente Paso

**🚀 READY TO DEPLOY!**

1. Ve a tu dashboard de Coolify
2. Sigue los pasos de arriba
3. ¡Tu servidor MCP estará funcionando en producción!

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en Coolify
2. Verifica las variables de entorno
3. Confirma la conectividad a Odoo
4. Consulta `DEPLOYMENT.md` para troubleshooting detallado

---
**¡El servidor está listo para producción!** 🎉

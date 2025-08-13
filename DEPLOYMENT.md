# 🚀 Deployment en Coolify

Esta guía te ayudará a hacer deploy del servidor MCP de Odoo en Coolify.

## 📋 Pre-requisitos

1. **Coolify instalado y funcionando**
2. **Acceso a tu instancia de Odoo**
3. **API keys** (Anthropic/OpenAI - opcional)
4. **Repositorio GitHub** configurado

## 🔧 Configuración en Coolify

### 1. Crear un nuevo proyecto

1. Ve a tu dashboard de Coolify
2. Clic en **"New Resource"**
3. Selecciona **"Application"**
4. Elige **"Public Repository"**

### 2. Configurar el repositorio

- **Git Repository**: `https://github.com/iaisep/odoo-mcp-server`
- **Branch**: `main`
- **Build Pack**: `Docker`
- **Dockerfile**: `./Dockerfile`

### 3. Configurar variables de entorno

#### Variables Requeridas:
```env
ODOO_URL=https://sunafront.universidadisep.com
ODOO_DB=UniversidadISep
ODOO_USERNAME=iallamadas@universidadisep.com
ODOO_PASSWORD=Veronica023_
```

#### Variables Opcionales:
```env
ANTHROPIC_API_KEY=tu_api_key_anthropic
OPENAI_API_KEY=tu_api_key_openai
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8083
DEV_MODE=false
MOCK_ODOO_DATA=false
```

#### Variables del MCP:
```env
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0
MCP_SERVER_DESCRIPTION=MCP Server para Odoo CRM/Partner con integración Anthropic
```

### 4. Configurar el puerto

- **Port**: `8083`
- **Health Check Path**: `/health` (si está habilitado)

### 5. Configurar dominio

- **Domain**: Asignar un subdominio (ej: `odoo-mcp.tudominio.com`)
- **SSL**: Habilitar certificado automático

## 🚀 Deploy

1. **Deploy**: Clic en "Deploy"
2. **Monitorear**: Ver logs en tiempo real
3. **Verificar**: Acceder a `https://tu-dominio.com/health`

## ✅ Verificación

### Health Check
```bash
curl https://tu-dominio.com/health
```

Respuesta esperada:
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

### Probar herramientas MCP
El servidor estará disponible en el endpoint configurado y listo para integrarse con n8n o cualquier cliente MCP.

## 🔧 Configuración de Red

### Firewall
- Puerto **8083** debe estar abierto
- HTTPS habilitado (certificado SSL)

### DNS
- Configurar el dominio para apuntar a tu servidor Coolify
- Certificado SSL automático via Let's Encrypt

## 📊 Monitoreo

### Logs
```bash
# Ver logs en Coolify Dashboard
# O conectar via SSH y ejecutar:
docker logs <container_name>
```

### Métricas
- CPU y memoria disponibles en Coolify dashboard
- Health checks automáticos cada 30 segundos

## 🛠️ Troubleshooting

### Error de conexión Odoo
1. Verificar variables de entorno
2. Probar conexión manual: `curl -X GET https://sunafront.universidadisep.com`
3. Revisar logs: buscar "Error conectando a Odoo"

### Error de Anthropic
1. Verificar API key
2. Confirmar créditos en cuenta Anthropic
3. Fallback a OpenAI si es necesario

### Error de puerto
1. Verificar que PORT=8083 esté configurado
2. Revisar que el puerto esté expuesto en Coolify
3. Verificar firewall/seguridad

## 🔄 Actualizaciones

Para actualizar el deployment:
1. Push cambios al repositorio GitHub
2. En Coolify: Trigger manual deploy o configurar auto-deploy
3. Monitorear logs durante el deployment

## 📞 Integración con n8n

Una vez deployado, el servidor estará disponible en:
```
https://tu-dominio.com
```

Configura n8n para usar este endpoint y tendrás acceso a todas las herramientas MCP del servidor Odoo.

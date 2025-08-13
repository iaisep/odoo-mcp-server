# 🔧 Configuración para Coolify Dashboard

## Variables de Entorno Requeridas:

```env
# Odoo Connection (REQUERIDAS)
ODOO_URL=https://sunafront.universidadisep.com
ODOO_DB=UniversidadISep
ODOO_USERNAME=iallamadas@universidadisep.com
ODOO_PASSWORD=Veronica023_

# Server Configuration (IMPORTANTES)
PORT=8000
HOST=0.0.0.0

# Optional (recomendadas)
LOG_LEVEL=INFO
DEV_MODE=false
MOCK_ODOO_DATA=false
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0

# API Keys (opcionales)
ANTHROPIC_API_KEY=tu_key_si_tienes
OPENAI_API_KEY=tu_key_si_tienes
```

## Configuración de Red en Coolify:

1. **Port**: `8000` (IMPORTANTE - cambió de 8083 a 8000)
2. **Health Check**: `/health`
3. **Build Command**: Automático (usa Dockerfile)

## Para Debug:

1. **Ve a Coolify Dashboard**
2. **Encuentra tu aplicación**
3. **Ve a "Logs"** para ver errores
4. **Ve a "Deployments"** para ver historial
5. **Trigger "Deploy"** para usar el código actualizado

## Checklist de Verificación:

- [ ] Puerto configurado como `8000` (no 8083)
- [ ] Variables de entorno todas configuradas
- [ ] Último código de GitHub desplegado
- [ ] Health check apuntando a `/health`
- [ ] Sin errores en los logs de deployment

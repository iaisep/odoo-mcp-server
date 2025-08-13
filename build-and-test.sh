#!/bin/bash

# 🐳 Script de construcción y testing para Docker
# Este script construye y prueba el contenedor Docker localmente antes del deploy

echo "🚀 Construyendo imagen Docker..."

# Construir imagen
docker build -t odoo-mcp-server:latest .

if [ $? -ne 0 ]; then
    echo "❌ Error construyendo imagen Docker"
    exit 1
fi

echo "✅ Imagen construida correctamente"

# Crear archivo .env local para testing (opcional)
if [ ! -f ".env.local" ]; then
    cat > .env.local << EOF
ODOO_URL=https://sunafront.universidadisep.com
ODOO_DB=UniversidadISep
ODOO_USERNAME=iallamadas@universidadisep.com
ODOO_PASSWORD=Veronica023_
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8083
DEV_MODE=false
MOCK_ODOO_DATA=false
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0
MCP_SERVER_DESCRIPTION=MCP Server para Odoo CRM/Partner con integración Anthropic
EOF
    echo "📁 Archivo .env.local creado. Edita las API keys si las tienes."
fi

echo "🔧 Iniciando contenedor para testing..."

# Ejecutar contenedor en background
docker run -d \
    --name odoo-mcp-server-test \
    --env-file .env.local \
    -p 8083:8083 \
    odoo-mcp-server:latest

if [ $? -ne 0 ]; then
    echo "❌ Error iniciando contenedor"
    exit 1
fi

echo "⏳ Esperando a que el servidor inicie..."
sleep 10

# Probar health check
echo "🔍 Probando health check..."
response=$(curl -s http://localhost:8083/health)

if [[ $response == *"healthy"* ]]; then
    echo "✅ Health check exitoso:"
    echo $response | python -m json.tool
else
    echo "❌ Health check falló:"
    echo $response
    echo ""
    echo "📋 Logs del contenedor:"
    docker logs odoo-mcp-server-test --tail 20
fi

echo ""
echo "📊 Estado del contenedor:"
docker ps | grep odoo-mcp-server-test

echo ""
echo "🧹 Para limpiar el testing:"
echo "docker stop odoo-mcp-server-test"
echo "docker rm odoo-mcp-server-test"
echo "docker rmi odoo-mcp-server:latest"

echo ""
echo "🚀 Si todo funciona correctamente, puedes hacer deploy en Coolify!"

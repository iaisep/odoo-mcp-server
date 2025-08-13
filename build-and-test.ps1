# 🐳 Script de construcción y testing para Docker (PowerShell)
# Este script construye y prueba el contenedor Docker localmente antes del deploy

Write-Host "🚀 Construyendo imagen Docker..." -ForegroundColor Green

# Construir imagen
docker build -t odoo-mcp-server:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error construyendo imagen Docker" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagen construida correctamente" -ForegroundColor Green

# Crear archivo .env.local local para testing (opcional)
if (-not (Test-Path ".env.local")) {
    $envContent = @"
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
"@
    $envContent | Out-File -FilePath ".env.local" -Encoding UTF8
    Write-Host "📁 Archivo .env.local creado. Edita las API keys si las tienes." -ForegroundColor Yellow
}

Write-Host "🔧 Iniciando contenedor para testing..." -ForegroundColor Green

# Ejecutar contenedor en background
docker run -d --name odoo-mcp-server-test --env-file .env.local -p 8083:8083 odoo-mcp-server:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error iniciando contenedor" -ForegroundColor Red
    exit 1
}

Write-Host "⏳ Esperando a que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Probar health check
Write-Host "🔍 Probando health check..." -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8083/health" -Method Get -TimeoutSec 10
    
    if ($response.status -eq "healthy") {
        Write-Host "✅ Health check exitoso:" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } else {
        Write-Host "❌ Health check falló:" -ForegroundColor Red
        $response | ConvertTo-Json -Depth 3
    }
} catch {
    Write-Host "❌ Error conectando al health check:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Logs del contenedor:" -ForegroundColor Yellow
    docker logs odoo-mcp-server-test --tail 20
}

Write-Host ""
Write-Host "📊 Estado del contenedor:" -ForegroundColor Cyan
docker ps | Select-String "odoo-mcp-server-test"

Write-Host ""
Write-Host "🧹 Para limpiar el testing:" -ForegroundColor Yellow
Write-Host "docker stop odoo-mcp-server-test" -ForegroundColor Gray
Write-Host "docker rm odoo-mcp-server-test" -ForegroundColor Gray
Write-Host "docker rmi odoo-mcp-server:latest" -ForegroundColor Gray

Write-Host ""
Write-Host "🚀 Si todo funciona correctamente, puedes hacer deploy en Coolify!" -ForegroundColor Green

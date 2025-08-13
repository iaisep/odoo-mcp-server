# MCP Server para Odoo CRM/Partner + Anthropic LLM

Este proyecto implementa un servidor MCP (Model Context Protocol) en Python que conecta con Odoo 16 vía XML-RPC para gestionar leads del CRM y partners, integrado con Anthropic Claude para procesamiento de lenguaje natural.

## 🚀 Características

- **Conexión con Odoo 16**: Interacción completa con modelos `crm_lead` y `res_partner`
- **Integración Anthropic**: Procesamiento de consultas en lenguaje natural
- **Servidor MCP completo**: Compatible con clientes MCP como Claude Desktop
- **Herramientas especializadas**: 12 herramientas para gestión completa de CRM

## 📋 Requisitos

- Python 3.8+
- Acceso a Odoo 16 con API XML-RPC habilitada
- API Key de Anthropic
- Cliente MCP (como Claude Desktop)

## ⚡ Instalación rápida

1. **Clonar y configurar entorno:**
```bash
git clone <tu-repo>
cd odoo-mcp-server
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

4. **Probar el servidor:**
```bash
python main.py
```

## 🔧 Configuración

### Variables de entorno (.env)

```env
# Odoo Configuration
ODOO_URL=https://tu-odoo-server.com
ODOO_DB=tu_base_de_datos
ODOO_USERNAME=tu_usuario
ODOO_PASSWORD=tu_password

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-api03-...

# MCP Configuration
MCP_SERVER_NAME=odoo-mcp-server
MCP_SERVER_VERSION=1.0.0
```

### Claude Desktop

Agregar en `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo-mcp-server": {
      "command": "python",
      "args": ["C:\\ruta\\completa\\al\\main.py"],
      "cwd": "C:\\ruta\\completa\\al\\directorio"
    }
  }
}
```

## 🛠️ Herramientas disponibles

### 🔍 Gestión de Leads
- `get_leads` - Consultar leads con filtros avanzados
- `create_lead` - Crear nuevos leads
- `update_lead` - Actualizar leads existentes

### 👥 Gestión de Partners
- `get_partners` - Consultar partners/contactos
- `create_partner` - Crear nuevos partners
- `update_partner` - Actualizar partners existentes

### 🤖 Inteligencia Artificial
- `natural_language_query` - Procesar consultas en lenguaje natural
- `interpret_odoo_action` - Convertir texto a acciones de Odoo

### 🎯 Herramientas auxiliares
- `test_connections` - Probar conectividad
- `get_crm_stages` - Obtener etapas del CRM
- `get_crm_teams` - Obtener equipos de ventas
- `get_countries` - Obtener lista de países

## 📊 Casos de uso específicos

### Contexto universitario
El servidor está optimizado para instituciones educativas con campos específicos:
- `x_studio_programa_academico` - Programa académico de interés
- `x_studio_canal_de_contacto` - Canal de primer contacto
- `x_studio_programa_de_inters` - Programa específico de interés
- `progress` - Progreso del proceso de admisión
- `manage_reason` - Motivo de gestión del lead

### Consultas inteligentes
```bash
# Ejemplos de consultas en lenguaje natural:
"Encuentra todos los leads interesados en ingeniería que no han sido contactados"
"Crea un lead para Juan Pérez interesado en Administración de Empresas"
"Actualiza el progreso del lead 123 al 75%"
```

## 🔗 Integración con modelos de datos

Basado en el diccionario de datos de UniversidadISep, el servidor maneja:

### Tabla `crm_lead` (103 campos)
- Información básica: name, contact_name, email_from, phone
- Ubicación: street, city, zip, country_id, state_id
- Comercial: user_id, team_id, stage_id, expected_revenue
- Universitario: programas académicos, canales de contacto

### Tabla `res_partner` (Múltiples campos)
- Contactos personales y empresas
- Jerarquías de contactos (parent_id)
- Categorización y segmentación
- Información comercial completa

## 🚦 Estados y flujo

1. **Lead** → Prospecto inicial
2. **Opportunity** → Oportunidad calificada  
3. **Won/Lost** → Ganada o perdida

## 🧪 Testing

```bash
# Probar conexiones
python -c "
from main import initialize_clients, test_connections
initialize_clients()
print(test_connections())
"

# Probar herramientas específicas
python -c "
from main import initialize_clients, get_leads
initialize_clients()
print(get_leads(limit=5))
"
```

## 📝 Logging

Los logs se envían a `stderr` (requerimiento MCP):
- Conexiones y errores de Odoo
- Respuestas de Anthropic
- Estado general del servidor

## 🔒 Seguridad

- Variables de entorno para credenciales
- Validación de parámetros de entrada
- Manejo seguro de conexiones XML-RPC
- Logs sin información sensible

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- Documentación: [MCP Protocol](https://modelcontextprotocol.io/)
- Issues: Abrir un issue en GitHub
- Odoo API: [Documentación oficial](https://www.odoo.com/documentation/16.0/developer/reference/external_api.html)
- Anthropic: [Documentación Claude](https://docs.anthropic.com/)

---

**¿Listo para potenciar tu CRM universitario con IA?** 🎓✨

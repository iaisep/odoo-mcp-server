# 🚀 Actualizaciones Masivas con Lenguaje Natural - Guía n8n

## 📋 Descripción General

Esta funcionalidad permite ejecutar actualizaciones masivas en registros de Odoo usando instrucciones en **lenguaje natural**, interpretadas por Claude AI. Es perfecta para automatizaciones en n8n que requieren modificaciones masivas de datos.

## 🔗 Endpoint

```
POST https://dev2.odoo.universidadisep.com/mcp/execute_natural_update
```

## 📝 Estructura del Payload

```json
{
  "instruction": "Instrucción en lenguaje natural",
  "model": "crm.lead",
  "dry_run": true,
  "max_records": 100
}
```

### Parámetros

- **`instruction`** (requerido): Instrucción en lenguaje natural sobre qué actualizar
- **`model`** (opcional): Modelo de Odoo a actualizar (defecto: "crm.lead")
- **`dry_run`** (opcional): Si es true, solo simula los cambios (defecto: true)
- **`max_records`** (opcional): Límite máximo de registros a procesar (defecto: 100)

## 🎯 Ejemplos de Instrucciones

### 1. Llenar Campos Vacíos
```json
{
  "instruction": "Llenar el campo email_from con 'info@universidad.edu.co' para todos los leads que tengan 'Universidad' en el nombre y email vacío",
  "model": "crm.lead",
  "dry_run": true,
  "max_records": 50
}
```

### 2. Actualizar por Ubicación
```json
{
  "instruction": "Actualizar el campo phone con '+57-1-555-0000' para todos los leads de Bogotá que no tengan teléfono",
  "model": "crm.lead", 
  "dry_run": true,
  "max_records": 25
}
```

### 3. Cambiar Estados por Fecha
```json
{
  "instruction": "Cambiar el stage_id a 2 para todos los leads creados en los últimos 7 días",
  "model": "crm.lead",
  "dry_run": true,
  "max_records": 100
}
```

### 4. Asignar por Campo Custom
```json
{
  "instruction": "Asignar user_id = 5 a todos los leads sin asignar que contengan 'Ingeniería' en x_studio_programa_de_inters",
  "model": "crm.lead",
  "dry_run": false,
  "max_records": 30
}
```

### 5. Actualizar Campos Custom
```json
{
  "instruction": "Cambiar x_studio_canal_de_contacto a 'Web' para todos los leads que tengan email pero no tengan canal de contacto definido",
  "model": "crm.lead",
  "dry_run": true,
  "max_records": 40
}
```

## 📊 Estructura de Respuesta

### Respuesta Exitosa (Dry Run)
```json
{
  "plan": {
    "action": "update",
    "model": "crm.lead",
    "search_criteria": [
      ["name", "ilike", "Universidad"],
      ["email_from", "=", false]
    ],
    "updates": {
      "email_from": "info@universidad.edu.co"
    },
    "description": "Actualizar campo email_from para leads con Universidad en nombre y email vacío",
    "estimated_impact": "Se actualizarían registros que coincidan con los criterios especificados"
  },
  "found_records": 15,
  "record_ids": [123, 124, 125, 126, 127],
  "preview_current_data": [
    {
      "id": 123,
      "name": "Universidad Nacional - Consulta",
      "email_from": false,
      "create_date": "2024-08-10 10:30:00"
    }
  ],
  "dry_run": true,
  "message": "SIMULACIÓN: Se actualizarían 15 registros. Use dry_run=False para ejecutar realmente.",
  "planned_updates": {
    "email_from": "info@universidad.edu.co"
  }
}
```

### Respuesta Exitosa (Ejecución Real)
```json
{
  "plan": {
    "action": "update",
    "model": "crm.lead", 
    "search_criteria": [
      ["city", "=", "Bogotá"],
      ["phone", "=", false]
    ],
    "updates": {
      "phone": "+57-1-555-0000"
    },
    "description": "Actualizar teléfono para leads de Bogotá sin teléfono"
  },
  "found_records": 8,
  "record_ids": [201, 202, 203, 204, 205, 206, 207, 208],
  "preview_current_data": [
    {
      "id": 201,
      "name": "Lead Bogotá 1",
      "city": "Bogotá",
      "phone": false
    }
  ],
  "preview_updated_data": [
    {
      "id": 201,
      "name": "Lead Bogotá 1", 
      "city": "Bogotá",
      "phone": "+57-1-555-0000"
    }
  ],
  "dry_run": false,
  "message": "✅ Actualización exitosa en 8 registros",
  "status": "success"
}
```

### Respuesta de Error
```json
{
  "error": "Error parseando plan de actualización: Expecting value: line 1 column 1 (char 0)",
  "raw_response": "La instrucción no pudo ser interpretada correctamente",
  "instruction": "instrucción inválida",
  "model": "crm.lead"
}
```

## 🛠️ Configuración en n8n

### 1. Nodo HTTP Request - Configuración Básica
- **Method**: POST
- **URL**: `https://dev2.odoo.universidadisep.com/mcp/execute_natural_update`
- **Authentication**: None (por ahora)
- **Body Content Type**: JSON

### 2. Body del Request
```json
{
  "instruction": "{{ $json.instruction }}",
  "model": "{{ $json.model || 'crm.lead' }}",
  "dry_run": {{ $json.dry_run || true }},
  "max_records": {{ $json.max_records || 100 }}
}
```

### 3. Headers
```json
{
  "Content-Type": "application/json"
}
```

## 🔄 Workflow de n8n Sugerido

### Flujo de Validación y Ejecución

1. **Trigger** → Ejecutar cada X tiempo o manualmente
2. **Set Node** → Definir instrucción y parámetros
3. **HTTP Request 1** → Ejecutar en modo `dry_run: true`
4. **IF Node** → Validar que `found_records > 0`
5. **Set Node 2** → Cambiar a `dry_run: false` si validación OK
6. **HTTP Request 2** → Ejecutar actualización real
7. **Slack/Email** → Notificar resultado

### Ejemplo de Configuración Set Node
```json
{
  "instruction": "Llenar el campo mobile con '+57-300-000-0000' para todos los leads que tengan email pero no tengan móvil",
  "model": "crm.lead",
  "dry_run": true,
  "max_records": 50
}
```

## ⚠️ Consideraciones de Seguridad

### Modo Dry Run (Recomendado)
- **Siempre usar** `dry_run: true` primero
- Validar que `found_records` sea el número esperado
- Revisar `preview_current_data` para confirmar registros correctos
- Solo entonces ejecutar con `dry_run: false`

### Límites de Seguridad
- `max_records` nunca debe ser > 500
- Para actualizaciones masivas grandes, dividir en lotes
- Siempre revisar el plan generado por Claude

### Campos Sensibles
- Tener cuidado con campos como `user_id`, `team_id`, `stage_id`
- Validar que los IDs de referencia existan en Odoo
- No modificar campos del sistema como `id`, `create_date`

## 📈 Casos de Uso Comunes

### 1. Normalización de Datos
```json
{
  "instruction": "Cambiar todos los valores 'SI' a 'Sí' en el campo x_studio_acepta_marketing",
  "dry_run": true
}
```

### 2. Asignación Automática
```json
{
  "instruction": "Asignar user_id = 3 a todos los leads de programas de Ingeniería que no estén asignados",
  "dry_run": true,
  "max_records": 100
}
```

### 3. Actualización de Estados
```json
{
  "instruction": "Mover a stage_id = 4 todos los leads en etapa 2 que tengan más de 30 días sin actividad",
  "dry_run": true
}
```

### 4. Enriquecimiento de Datos
```json
{
  "instruction": "Llenar el campo website con 'https://www.universidadisep.com' para todos los leads que no tengan website",
  "dry_run": true,
  "max_records": 200
}
```

## 🧪 Testing

Usar el script de prueba incluido:
```bash
python test_natural_update.py
```

Este script incluye varios casos de prueba predefinidos para validar la funcionalidad.

## 📞 Soporte

- Revisar logs del servidor para debugging
- Validar sintaxis de instrucciones con Claude
- Usar modo dry_run para testing seguro

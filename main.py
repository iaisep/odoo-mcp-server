#!/usr/bin/env python3
"""
Servidor MCP para Odoo CRM/Partner con integración Anthropic
"""

import os
import sys
import asyncio
import logging
import threading
import time
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Importar nuestros módulos
from odoo_client import OdooClient
from anthropic_client import AnthropicClient
from models import (
    LeadData, PartnerData, LeadSearchFilters, PartnerSearchFilters,
    NaturalLanguageQuery, OdooResponse, AnthropicResponse
)

# Cargar variables de entorno
load_dotenv()

# Configurar logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # MCP servers deben usar stderr para logs
    ]
)
logger = logging.getLogger(__name__)

# Inicializar FastMCP
app = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "odoo-mcp-server")
)

# Inicializar FastAPI para health checks
health_app = FastAPI(title="Odoo MCP Server Health")

# Función helper para serialización JSON segura con datetime
def safe_json_dumps(data, **kwargs):
    """
    Serializar datos a JSON aplicando serialización datetime automáticamente
    """
    try:
        from odoo_client import serialize_datetime_objects
        serialized_data = serialize_datetime_objects(data)
        return json.dumps(serialized_data, **kwargs)
    except Exception as e:
        logger.error(f"Error en serialización JSON: {str(e)}")
        return json.dumps({"error": f"Serialization error: {str(e)}"}, ensure_ascii=False)

# Clientes globales
odoo_client: Optional[OdooClient] = None
anthropic_client: Optional[AnthropicClient] = None

def initialize_clients():
    """Inicializar clientes de Odoo y Anthropic"""
    global odoo_client, anthropic_client
    
    try:
        # Inicializar cliente Odoo
        odoo_url = os.getenv("ODOO_URL")
        odoo_db = os.getenv("ODOO_DB")
        odoo_username = os.getenv("ODOO_USERNAME")
        odoo_password = os.getenv("ODOO_PASSWORD")
        
        if not all([odoo_url, odoo_db, odoo_username, odoo_password]):
            raise ValueError("Faltan variables de entorno para Odoo")
        
        odoo_client = OdooClient(odoo_url, odoo_db, odoo_username, odoo_password)
        logger.info("Cliente Odoo inicializado exitosamente")
        
        # Inicializar cliente Anthropic
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("Falta ANTHROPIC_API_KEY")
        
        anthropic_client = AnthropicClient(anthropic_api_key)
        logger.info("Cliente Anthropic inicializado exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando clientes: {str(e)}")
        sys.exit(1)

# =================== HERRAMIENTAS MCP ===================

@app.tool()
def test_connections() -> str:
    """
    Probar conexiones con Odoo y Anthropic
    
    Returns:
        str: Resultado de las pruebas de conexión
    """
    results = {}
    
    # Probar Odoo
    if odoo_client:
        odoo_test = odoo_client.test_connection()
        results["odoo"] = {
            "success": odoo_test.success,
            "message": odoo_test.message,
            "error": odoo_test.error
        }
    else:
        results["odoo"] = {"success": False, "message": "Cliente Odoo no inicializado"}
    
    # Probar Anthropic
    if anthropic_client:
        try:
            test_query = NaturalLanguageQuery(query="Test connection", max_tokens=10)
            anthropic_test = anthropic_client.process_natural_language_query(test_query)
            results["anthropic"] = {
                "success": True,
                "message": "Conexión exitosa",
                "model": anthropic_test.model
            }
        except Exception as e:
            results["anthropic"] = {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    else:
        results["anthropic"] = {"success": False, "message": "Cliente Anthropic no inicializado"}
    
    return json.dumps(results, indent=2, ensure_ascii=False)

@app.tool()
def get_leads(
    stage_id: Optional[int] = None,
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    email_from: Optional[str] = None,
    partner_name: Optional[str] = None,
    contact_name: Optional[str] = None,
    city: Optional[str] = None,
    country_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Obtener leads del CRM de Odoo
    
    Args:
        stage_id: ID de la etapa del CRM
        user_id: ID del vendedor asignado
        team_id: ID del equipo de ventas
        type: Tipo de lead ('lead' o 'opportunity')
        priority: Prioridad ('0'=Low, '1'=Normal, '2'=High, '3'=Urgent)
        email_from: Email del contacto (búsqueda parcial)
        partner_name: Nombre de la empresa (búsqueda parcial)
        contact_name: Nombre del contacto (búsqueda parcial)
        city: Ciudad (búsqueda parcial)
        country_id: ID del país
        limit: Número máximo de resultados (default: 10)
        offset: Número de resultados a saltar (default: 0)
    
    Returns:
        str: JSON con los leads encontrados
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    filters = LeadSearchFilters(
        stage_id=stage_id,
        user_id=user_id,
        team_id=team_id,
        type=type,
        priority=priority,
        email_from=email_from,
        partner_name=partner_name,
        contact_name=contact_name,
        city=city,
        country_id=country_id,
        limit=limit,
        offset=offset
    )
    
    result = odoo_client.get_leads(filters)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def create_lead(
    name: str,
    contact_name: Optional[str] = None,
    partner_name: Optional[str] = None,
    email_from: Optional[str] = None,
    phone: Optional[str] = None,
    mobile: Optional[str] = None,
    website: Optional[str] = None,
    function: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None,
    zip: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    priority: Optional[str] = None,
    expected_revenue: Optional[float] = None,
    probability: Optional[float] = None,
    description: Optional[str] = None,
    type: str = "lead",
    x_studio_programa_academico: Optional[int] = None,
    x_studio_canal_de_contacto: Optional[str] = None,
    x_studio_programa_de_inters: Optional[str] = None,
    manage_reason: Optional[str] = None,
    action_request_lead: Optional[str] = None
) -> str:
    """
    Crear un nuevo lead en el CRM
    
    Args:
        name: Nombre de la oportunidad (requerido)
        contact_name: Nombre del contacto
        partner_name: Nombre de la empresa
        email_from: Email del contacto
        phone: Teléfono
        mobile: Móvil
        website: Sitio web
        function: Cargo/Posición
        street: Dirección
        city: Ciudad
        zip: Código postal
        country_id: ID del país
        state_id: ID del estado
        user_id: ID del vendedor
        team_id: ID del equipo de ventas
        stage_id: ID de la etapa
        priority: Prioridad ('0'=Low, '1'=Normal, '2'=High, '3'=Urgent)
        expected_revenue: Ingresos esperados
        probability: Probabilidad de cierre (0-100)
        description: Notas
        type: Tipo ('lead' o 'opportunity')
        x_studio_programa_academico: ID del programa académico
        x_studio_canal_de_contacto: Canal de contacto
        x_studio_programa_de_inters: Programa de interés
        manage_reason: Motivo de gestión
        action_request_lead: Acción solicitada por lead
    
    Returns:
        str: JSON con el resultado de la creación
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    lead_data = LeadData(
        name=name,
        contact_name=contact_name,
        partner_name=partner_name,
        email_from=email_from,
        phone=phone,
        mobile=mobile,
        website=website,
        function=function,
        street=street,
        city=city,
        zip=zip,
        country_id=country_id,
        state_id=state_id,
        user_id=user_id,
        team_id=team_id,
        stage_id=stage_id,
        priority=priority,
        expected_revenue=expected_revenue,
        probability=probability,
        description=description,
        type=type,
        x_studio_programa_academico=x_studio_programa_academico,
        x_studio_canal_de_contacto=x_studio_canal_de_contacto,
        x_studio_programa_de_inters=x_studio_programa_de_inters,
        manage_reason=manage_reason,
        action_request_lead=action_request_lead
    )
    
    result = odoo_client.create_lead(lead_data)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def update_lead(
    lead_id: int,
    name: Optional[str] = None,
    contact_name: Optional[str] = None,
    partner_name: Optional[str] = None,
    email_from: Optional[str] = None,
    phone: Optional[str] = None,
    mobile: Optional[str] = None,
    website: Optional[str] = None,
    function: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None,
    zip: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    priority: Optional[str] = None,
    expected_revenue: Optional[float] = None,
    probability: Optional[float] = None,
    description: Optional[str] = None,
    type: Optional[str] = None,
    x_studio_programa_academico: Optional[int] = None,
    x_studio_canal_de_contacto: Optional[str] = None,
    x_studio_programa_de_inters: Optional[str] = None,
    progress: Optional[float] = None,
    manage_reason: Optional[str] = None,
    action_request_lead: Optional[str] = None
) -> str:
    """
    Actualizar un lead existente
    
    Args:
        lead_id: ID del lead a actualizar (requerido)
        name: Nombre de la oportunidad
        contact_name: Nombre del contacto
        partner_name: Nombre de la empresa
        email_from: Email del contacto
        phone: Teléfono
        mobile: Móvil
        website: Sitio web
        function: Cargo/Posición
        street: Dirección
        city: Ciudad
        zip: Código postal
        country_id: ID del país
        state_id: ID del estado
        user_id: ID del vendedor
        team_id: ID del equipo de ventas
        stage_id: ID de la etapa
        priority: Prioridad ('0'=Low, '1'=Normal, '2'=High, '3'=Urgent)
        expected_revenue: Ingresos esperados
        probability: Probabilidad de cierre (0-100)
        description: Notas
        type: Tipo ('lead' o 'opportunity')
        x_studio_programa_academico: ID del programa académico
        x_studio_canal_de_contacto: Canal de contacto
        x_studio_programa_de_inters: Programa de interés
        progress: Progreso (0-100)
        manage_reason: Motivo de gestión
        action_request_lead: Acción solicitada por lead
    
    Returns:
        str: JSON con el resultado de la actualización
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    # Solo incluir campos que no son None
    lead_data = LeadData(
        name=name or "temp",  # name es requerido, usamos temp si es None
        contact_name=contact_name,
        partner_name=partner_name,
        email_from=email_from,
        phone=phone,
        mobile=mobile,
        website=website,
        function=function,
        street=street,
        city=city,
        zip=zip,
        country_id=country_id,
        state_id=state_id,
        user_id=user_id,
        team_id=team_id,
        stage_id=stage_id,
        priority=priority,
        expected_revenue=expected_revenue,
        probability=probability,
        description=description,
        type=type,
        x_studio_programa_academico=x_studio_programa_academico,
        x_studio_canal_de_contacto=x_studio_canal_de_contacto,
        x_studio_programa_de_inters=x_studio_programa_de_inters,
        progress=progress,
        manage_reason=manage_reason,
        action_request_lead=action_request_lead
    )
    
    # Si name era None, lo excluimos del dict final
    if name is None:
        # Creamos el dict excluyendo name
        update_dict = lead_data.model_dump(exclude_none=True)
        update_dict.pop('name', None)
        # Creamos un objeto LeadData temporal solo con los campos a actualizar
        filtered_data = LeadData(name="temp", **{k: v for k, v in update_dict.items() if k != 'name'})
    else:
        filtered_data = lead_data
    
    result = odoo_client.update_lead(lead_id, filtered_data)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def get_partners(
    is_company: Optional[bool] = None,
    customer_rank: Optional[int] = None,
    supplier_rank: Optional[int] = None,
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    city: Optional[str] = None,
    country_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    active: bool = True,
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Obtener partners (contactos/empresas) de Odoo
    
    Args:
        is_company: True si es empresa, False si es persona
        customer_rank: Rango de cliente (>= valor especificado)
        supplier_rank: Rango de proveedor (>= valor especificado)
        user_id: ID del vendedor responsable
        category_id: ID de categoría de partner
        city: Ciudad (búsqueda parcial)
        country_id: ID del país
        name: Nombre (búsqueda parcial)
        email: Email (búsqueda parcial)
        active: Solo partners activos (default: True)
        limit: Número máximo de resultados (default: 10)
        offset: Número de resultados a saltar (default: 0)
    
    Returns:
        str: JSON con los partners encontrados
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    filters = PartnerSearchFilters(
        is_company=is_company,
        customer_rank=customer_rank,
        supplier_rank=supplier_rank,
        user_id=user_id,
        category_id=category_id,
        city=city,
        country_id=country_id,
        name=name,
        email=email,
        active=active,
        limit=limit,
        offset=offset
    )
    
    result = odoo_client.get_partners(filters)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def create_partner(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    mobile: Optional[str] = None,
    website: Optional[str] = None,
    is_company: bool = False,
    parent_id: Optional[int] = None,
    street: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    zip: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    function: Optional[str] = None,
    title: Optional[int] = None,
    user_id: Optional[int] = None,
    vat: Optional[str] = None,
    ref: Optional[str] = None,
    lang: Optional[str] = None,
    customer_rank: int = 0,
    supplier_rank: int = 0
) -> str:
    """
    Crear un nuevo partner (contacto/empresa)
    
    Args:
        name: Nombre del partner (requerido)
        email: Email
        phone: Teléfono
        mobile: Móvil
        website: Sitio web
        is_company: True si es empresa, False si es persona
        parent_id: ID del partner padre (para contactos de empresas)
        street: Dirección
        street2: Dirección 2
        city: Ciudad
        zip: Código postal
        country_id: ID del país
        state_id: ID del estado
        function: Cargo/Posición
        title: ID del título (Sr., Sra., etc.)
        user_id: ID del vendedor responsable
        vat: NIT/RUT
        ref: Referencia interna
        lang: Idioma (ej: 'es_ES', 'en_US')
        customer_rank: Rango de cliente (default: 0)
        supplier_rank: Rango de proveedor (default: 0)
    
    Returns:
        str: JSON con el resultado de la creación
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    partner_data = PartnerData(
        name=name,
        email=email,
        phone=phone,
        mobile=mobile,
        website=website,
        is_company=is_company,
        parent_id=parent_id,
        street=street,
        street2=street2,
        city=city,
        zip=zip,
        country_id=country_id,
        state_id=state_id,
        function=function,
        title=title,
        user_id=user_id,
        vat=vat,
        ref=ref,
        lang=lang,
        customer_rank=customer_rank,
        supplier_rank=supplier_rank
    )
    
    result = odoo_client.create_partner(partner_data)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def update_partner(
    partner_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    mobile: Optional[str] = None,
    website: Optional[str] = None,
    is_company: Optional[bool] = None,
    parent_id: Optional[int] = None,
    street: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    zip: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    function: Optional[str] = None,
    title: Optional[int] = None,
    user_id: Optional[int] = None,
    vat: Optional[str] = None,
    ref: Optional[str] = None,
    lang: Optional[str] = None,
    customer_rank: Optional[int] = None,
    supplier_rank: Optional[int] = None,
    active: Optional[bool] = None
) -> str:
    """
    Actualizar un partner existente
    
    Args:
        partner_id: ID del partner a actualizar (requerido)
        name: Nombre del partner
        email: Email
        phone: Teléfono
        mobile: Móvil
        website: Sitio web
        is_company: True si es empresa, False si es persona
        parent_id: ID del partner padre
        street: Dirección
        street2: Dirección 2
        city: Ciudad
        zip: Código postal
        country_id: ID del país
        state_id: ID del estado
        function: Cargo/Posición
        title: ID del título
        user_id: ID del vendedor responsable
        vat: NIT/RUT
        ref: Referencia interna
        lang: Idioma
        customer_rank: Rango de cliente
        supplier_rank: Rango de proveedor
        active: Activo/Inactivo
    
    Returns:
        str: JSON con el resultado de la actualización
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    partner_data = PartnerData(
        name=name or "temp",  # name es requerido
        email=email,
        phone=phone,
        mobile=mobile,
        website=website,
        is_company=is_company or False,
        parent_id=parent_id,
        street=street,
        street2=street2,
        city=city,
        zip=zip,
        country_id=country_id,
        state_id=state_id,
        function=function,
        title=title,
        user_id=user_id,
        vat=vat,
        ref=ref,
        lang=lang,
        customer_rank=customer_rank or 0,
        supplier_rank=supplier_rank or 0,
        active=active if active is not None else True
    )
    
    # Si name era None, lo excluimos del dict final
    if name is None:
        update_dict = partner_data.model_dump(exclude_none=True)
        update_dict.pop('name', None)
        filtered_data = PartnerData(name="temp", **{k: v for k, v in update_dict.items() if k != 'name'})
    else:
        filtered_data = partner_data
    
    result = odoo_client.update_partner(partner_id, filtered_data)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def execute_natural_update(
    instruction: str,
    model: str = "crm.lead",
    dry_run: bool = True,
    max_records: int = 100
) -> str:
    """
    Ejecuta actualizaciones masivas en registros basadas en instrucciones en lenguaje natural
    
    Args:
        instruction: Instrucción en lenguaje natural sobre qué actualizar
        model: Modelo de Odoo a actualizar (por defecto 'crm.lead')
        dry_run: Si True, solo simula los cambios sin aplicarlos
        max_records: Máximo número de registros a procesar (por seguridad)
    
    Returns:
        str: JSON con el plan de actualización y resultado
        
    Ejemplos de instrucciones:
    - "Llenar el campo email_from con 'contacto@universidad.edu' para todos los leads que tengan 'Universidad' en el nombre y email vacío"
    - "Actualizar el campo phone con '+57-1-555-0000' para todos los registros de Bogotá que no tengan teléfono"
    - "Cambiar el stage_id a 2 para todos los leads creados esta semana"
    """
    try:
        if not odoo_client or not anthropic_client:
            return json.dumps({"error": "Clientes no inicializados"})
            
        logger.info(f"Ejecutando actualización natural: {instruction}")
        
        # Usar Claude para interpretar la instrucción y generar el plan
        interpretation_prompt = f"""
Analiza esta instrucción para actualización masiva de registros en Odoo:

INSTRUCCIÓN: "{instruction}"
MODELO: {model}
LÍMITE: {max_records} registros

Tu tarea es generar un plan de actualización estructurado. Responde SOLO con un JSON válido con esta estructura:

{{
    "action": "update",
    "model": "{model}",
    "search_criteria": [
        // Criterios de búsqueda para encontrar registros a actualizar
        // Formato: ["campo", "operador", "valor"]
        // Operadores: =, !=, ilike, not ilike, in, not in, >, <, >=, <=
    ],
    "updates": {{
        // Campos a actualizar con sus nuevos valores
        "campo1": "valor1",
        "campo2": "valor2"
    }},
    "description": "Descripción clara de qué se va a hacer",
    "estimated_impact": "Descripción del impacto esperado"
}}

IMPORTANTE:
- Para campos de texto usa "ilike" para búsquedas parciales
- Para campos vacíos usa ["campo", "=", false]
- Para campos no vacíos usa ["campo", "!=", false]
- Los valores deben ser del tipo correcto (str, int, float, bool)
- Sé específico con los criterios para evitar actualizaciones no deseadas

Ejemplos de search_criteria:
- Buscar registros con nombre que contenga "Universidad": ["name", "ilike", "Universidad"]
- Buscar registros con email vacío: ["email_from", "=", false]
- Buscar registros creados hoy: ["create_date", ">=", "2024-01-01"]
- Buscar registros de una ciudad específica: ["city", "=", "Bogotá"]
"""

        # Obtener interpretación de Claude
        interpretation_response = anthropic_client.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": interpretation_prompt}]
        )
        
        interpretation_text = interpretation_response.content[0].text.strip()
        
        try:
            # Parsear la respuesta JSON
            update_plan = json.loads(interpretation_text)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Error parseando plan de actualización: {e}",
                "raw_response": interpretation_text
            })
        
        # Validar estructura del plan
        required_fields = ["search_criteria", "updates", "description"]
        for field in required_fields:
            if field not in update_plan:
                return json.dumps({"error": f"Plan inválido: falta campo '{field}'"})
        
        # Buscar registros que coincidan con los criterios
        logger.info(f"Buscando registros con criterios: {update_plan['search_criteria']}")
        
        # Convertir criterios de búsqueda al formato de Odoo
        domain = update_plan['search_criteria']
        
        # Buscar registros
        record_ids = odoo_client.search_records(model, domain, limit=max_records)
        
        if not record_ids:
            return safe_json_dumps({
                "plan": update_plan,
                "found_records": 0,
                "message": "No se encontraron registros que coincidan con los criterios"
            })
        
        logger.info(f"Encontrados {len(record_ids)} registros para actualizar")
        
        # Obtener datos actuales de algunos registros para preview
        preview_records = odoo_client.get_records(model, record_ids[:5])  # Solo primeros 5 para preview
        
        result = {
            "plan": update_plan,
            "found_records": len(record_ids),
            "record_ids": record_ids,
            "preview_current_data": preview_records[:3],  # Solo 3 para no sobrecargar
            "dry_run": dry_run
        }
        
        if dry_run:
            result["message"] = f"SIMULACIÓN: Se actualizarían {len(record_ids)} registros. Use dry_run=False para ejecutar realmente."
            result["planned_updates"] = update_plan["updates"]
        else:
            # Ejecutar actualización real
            logger.info(f"Ejecutando actualización real en {len(record_ids)} registros")
            
            success = odoo_client.update_records(model, record_ids, update_plan["updates"])
            
            if success:
                result["message"] = f"✅ Actualización exitosa en {len(record_ids)} registros"
                result["status"] = "success"
                
                # Obtener datos actualizados de algunos registros para confirmación
                updated_records = odoo_client.get_records(model, record_ids[:3])
                result["preview_updated_data"] = updated_records
            else:
                result["message"] = "❌ Error durante la actualización"
                result["status"] = "error"
        
        return safe_json_dumps(result)
        
    except Exception as e:
        logger.error(f"Error en execute_natural_update: {e}")
        return safe_json_dumps({
            "error": str(e),
            "instruction": instruction,
            "model": model
        })

@app.tool()
def natural_language_query(query: str, context: Optional[str] = None, max_tokens: int = 1000) -> str:
    """
    Procesar una consulta en lenguaje natural usando Anthropic Claude
    
    Args:
        query: Consulta en lenguaje natural (requerido)
        context: Contexto adicional para la consulta
        max_tokens: Máximo número de tokens en la respuesta (default: 1000)
    
    Returns:
        str: Respuesta procesada por Claude
    """
    if not anthropic_client:
        return json.dumps({"error": "Cliente Anthropic no disponible"}, ensure_ascii=False)
    
    # Preparar contexto
    query_context = {}
    if context:
        try:
            # Intentar parsear como JSON
            query_context = json.loads(context)
        except:
            # Si no es JSON, usar como texto
            query_context = {"additional_context": context}
    
    nl_query = NaturalLanguageQuery(
        query=query,
        context=query_context,
        max_tokens=max_tokens
    )
    
    result = anthropic_client.process_natural_language_query(nl_query)
    
    # USAR FUNCIÓN HELPER PARA SERIALIZACIÓN SEGURA
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def interpret_odoo_action(query: str, context: Optional[str] = None) -> str:
    """
    Interpretar una consulta y sugerir qué acción realizar en Odoo
    
    Args:
        query: Consulta del usuario (requerido)
        context: Contexto adicional como JSON string
    
    Returns:
        str: JSON con la acción sugerida para Odoo
    """
    if not anthropic_client:
        return json.dumps({"error": "Cliente Anthropic no disponible"}, ensure_ascii=False)
    
    # Preparar contexto
    query_context = None
    if context:
        try:
            query_context = json.loads(context)
        except:
            query_context = {"raw_context": context}
    
    result = anthropic_client.interpret_odoo_action(query, query_context)
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def get_crm_stages() -> str:
    """
    Obtener las etapas del CRM
    
    Returns:
        str: JSON con las etapas disponibles
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    result = odoo_client.get_crm_stages()
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def get_crm_teams() -> str:
    """
    Obtener los equipos de ventas del CRM
    
    Returns:
        str: JSON con los equipos disponibles
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    result = odoo_client.get_crm_teams()
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

@app.tool()
def get_countries() -> str:
    """
    Obtener lista de países disponibles en Odoo
    
    Returns:
        str: JSON con los países disponibles
    """
    if not odoo_client:
        return json.dumps({"error": "Cliente Odoo no disponible"}, ensure_ascii=False)
    
    result = odoo_client.get_countries()
    return safe_json_dumps(result.model_dump(), indent=2, ensure_ascii=False)

# =================== INICIALIZACIÓN ===================

@app.tool()
def health_check() -> str:
    """
    Health check endpoint para verificar el estado del servidor
    
    Returns:
        str: JSON con el estado del servidor
    """
    try:
        status = {
            "status": "healthy",
            "service": "odoo-mcp-server",
            "version": os.getenv('MCP_SERVER_VERSION', '1.0.0'),
            "odoo_connected": bool(odoo_client and odoo_client.uid),
            "anthropic_available": bool(anthropic_client),
            "timestamp": str(asyncio.get_event_loop().time())
        }
        return json.dumps(status, indent=2, ensure_ascii=False)
    except Exception as e:
        error_status = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(asyncio.get_event_loop().time())
        }
        return json.dumps(error_status, indent=2, ensure_ascii=False)

# =================== HEALTH CHECK HTTP ENDPOINT ===================

@health_app.get("/health")
async def http_health_check():
    """
    HTTP Health check endpoint para Coolify y otros sistemas de monitoreo
    """
    try:
        status = {
            "status": "healthy",
            "service": "odoo-mcp-server",
            "version": os.getenv('MCP_SERVER_VERSION', '1.0.0'),
            "odoo_connected": bool(odoo_client and odoo_client.uid),
            "anthropic_available": bool(anthropic_client),
            "timestamp": str(time.time())
        }
        return JSONResponse(content=status)
    except Exception as e:
        error_status = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(time.time())
        }
        return JSONResponse(content=error_status, status_code=503)

@health_app.get("/")
async def root():
    """
    Root endpoint
    """
    # Verificar si la corrección datetime está disponible
    try:
        from odoo_client import serialize_datetime_objects
        datetime_fix_available = True
        from datetime import datetime
        test_datetime = datetime.now()
        test_serialized = serialize_datetime_objects(test_datetime)
        datetime_fix_working = isinstance(test_serialized, str)
    except Exception as e:
        datetime_fix_available = False
        datetime_fix_working = False
    
    return JSONResponse(content={
        "message": "Odoo MCP Server",
        "status": "running",
        "version": "1.1.0-datetime-fix",
        "deployment_time": str(time.time()),
        "datetime_fix_available": datetime_fix_available,
        "datetime_fix_working": datetime_fix_working,
        "health_endpoint": "/health",
        "debug_endpoint": "/debug",
        "mcp_tools": [
            "get_leads", "create_lead", "update_lead", 
            "get_partners", "create_partner", "natural_language_query"
        ]
    })

@health_app.get("/debug")
async def debug_info():
    """
    Debug endpoint para verificar el estado de las correcciones
    """
    try:
        from odoo_client import serialize_datetime_objects
        from datetime import datetime
        
        # Test de serialización datetime
        test_obj = {
            'datetime_field': datetime.now(),
            'regular_field': 'test',
            'nested': {
                'inner_date': datetime.now(),
                'inner_text': 'nested'
            }
        }
        
        serialized = serialize_datetime_objects(test_obj)
        
        return JSONResponse(content={
            "datetime_fix_status": "✅ WORKING",
            "function_available": True,
            "test_original": str(test_obj),
            "test_serialized": serialized,
            "all_dates_are_strings": all(
                isinstance(v, str) for k, v in serialized.items() 
                if 'date' in k.lower()
            ),
            "git_commit": "93c9e80 - datetime fix applied",
            "deployment_check": "This debug endpoint is new - if you see this, the latest code is deployed"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "datetime_fix_status": "❌ ERROR",
                "error": str(e),
                "function_available": False
            },
            status_code=500
        )

@health_app.post("/mcp/get_leads")
async def http_get_leads(filters: dict = None):
    """HTTP endpoint para obtener leads"""
    try:
        # ¡LLAMAR DIRECTAMENTE AL CLIENTE ODOO EN LUGAR DE LA FUNCIÓN MCP!
        from models import LeadSearchFilters
        
        # Extraer filtros
        stage_id = filters.get('stage_id') if filters else None
        user_id = filters.get('user_id') if filters else None
        team_id = filters.get('team_id') if filters else None
        limit = filters.get('limit', 10) if filters else 10
        
        # Crear filtros
        search_filters = LeadSearchFilters(
            stage_id=stage_id,
            user_id=user_id,
            team_id=team_id,
            limit=limit
        )
        
        # Llamar directamente al cliente Odoo (que YA tiene serialización datetime)
        if odoo_client:
            result = odoo_client.get_leads(search_filters)
            # result.model_dump() ya tiene datetime serializado gracias a nuestro fix
            return JSONResponse(content=result.model_dump())
        else:
            return JSONResponse(content={"error": "Cliente Odoo no disponible"}, status_code=503)
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@health_app.post("/mcp/create_lead")  
async def http_create_lead(lead_data: dict):
    """HTTP endpoint para crear leads"""
    try:
        from models import LeadData
        
        # Crear objeto LeadData
        lead = LeadData(**lead_data)
        
        # Llamar directamente al cliente Odoo
        if odoo_client:
            result = odoo_client.create_lead(lead)
            return JSONResponse(content=result.model_dump())
        else:
            return JSONResponse(content={"error": "Cliente Odoo no disponible"}, status_code=503)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@health_app.post("/mcp/get_partners")
async def http_get_partners(filters: dict = None):
    """HTTP endpoint para obtener partners"""
    try:
        from models import PartnerSearchFilters
        
        is_company = filters.get('is_company') if filters else None
        country_id = filters.get('country_id') if filters else None
        category_ids = filters.get('category_ids') if filters else None
        limit = filters.get('limit', 10) if filters else 10
        
        # Crear filtros
        search_filters = PartnerSearchFilters(
            is_company=is_company,
            country_id=country_id,
            category_ids=category_ids,
            limit=limit
        )
        
        # Llamar directamente al cliente Odoo
        if odoo_client:
            result = odoo_client.get_partners(search_filters)
            return JSONResponse(content=result.model_dump())
        else:
            return JSONResponse(content={"error": "Cliente Odoo no disponible"}, status_code=503)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@health_app.post("/mcp/natural_query")
async def http_natural_query(query_data: dict):
    """HTTP endpoint para consultas en lenguaje natural"""
    try:
        query = query_data.get('query', '')
        context = query_data.get('context', '')
        
        # Esta función devuelve directamente resultado de Anthropic, no hay datetime aquí
        # Pero por consistencia, mantener la estructura similar
        result = natural_language_query(query, context)
        parsed_result = json.loads(result)
        return JSONResponse(content=parsed_result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@health_app.post("/mcp/execute_natural_update")
async def http_execute_natural_update(update_data: dict):
    """HTTP endpoint para actualizaciones masivas con lenguaje natural"""
    try:
        instruction = update_data.get('instruction', '')
        model = update_data.get('model', 'crm.lead')
        dry_run = update_data.get('dry_run', True)
        max_records = update_data.get('max_records', 100)
        
        if not instruction:
            return JSONResponse(
                content={"error": "El campo 'instruction' es requerido"}, 
                status_code=400
            )
        
        # Ejecutar la actualización natural
        result = execute_natural_update(instruction, model, dry_run, max_records)
        parsed_result = json.loads(result)
        return JSONResponse(content=parsed_result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def main():
    """Función principal - Servidor HTTP permanente para Coolify"""
    try:
        logger.info("Iniciando Odoo MCP Server como servidor HTTP")
        
        # Inicializar clientes
        initialize_clients()
        
        logger.info("Clientes inicializados. Servidor listo para recibir peticiones HTTP.")
        
        # Configurar servidor HTTP
        port = int(os.getenv('PORT', 8001))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Iniciando servidor HTTP permanente en {host}:{port}")
        logger.info("Endpoints disponibles:")
        logger.info("  GET  /health - Health check")
        logger.info("  GET  / - Información del servidor")
        logger.info("  POST /mcp/get_leads - Obtener leads")
        logger.info("  POST /mcp/create_lead - Crear lead")
        logger.info("  POST /mcp/get_partners - Obtener partners")
        logger.info("  POST /mcp/natural_query - Consulta en lenguaje natural")
        logger.info("  POST /mcp/execute_natural_update - Actualizaciones masivas con lenguaje natural")
        
        # Ejecutar servidor HTTP como proceso principal (no daemon)
        uvicorn.run(
            health_app, 
            host=host, 
            port=port, 
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
    except Exception as e:
        logger.error(f"Error crítico en main(): {e}")
        logger.exception("Detalles del error:")
        raise

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Servidor MCP para Odoo CRM/Partner con integración Anthropic
"""

import os
import sys
import asyncio
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import json

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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # MCP servers deben usar stderr para logs
    ]
)
logger = logging.getLogger(__name__)

# Inicializar FastMCP
app = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "odoo-mcp-server"),
    version=os.getenv("MCP_SERVER_VERSION", "1.0.0")
)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    x_studio_programa_de_interes: Optional[str] = None,
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
        x_studio_programa_de_interes: Programa de interés
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
        x_studio_programa_de_interes=x_studio_programa_de_interes,
        manage_reason=manage_reason,
        action_request_lead=action_request_lead
    )
    
    result = odoo_client.create_lead(lead_data)
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    x_studio_programa_de_interes: Optional[str] = None,
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
        x_studio_programa_de_interes: Programa de interés
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
        x_studio_programa_de_interes=x_studio_programa_de_interes,
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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

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
    return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)

# =================== INICIALIZACIÓN ===================

def main():
    """Función principal del servidor MCP"""
    logger.info("Iniciando servidor MCP Odoo + Anthropic")
    
    # Inicializar clientes
    initialize_clients()
    
    # Ejecutar servidor MCP
    logger.info("Servidor MCP listo para recibir conexiones")
    app.run()

if __name__ == "__main__":
    main()

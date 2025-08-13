from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class LeadData(BaseModel):
    """Modelo para datos de Lead/Opportunity del CRM"""
    id: Optional[int] = None
    name: str = Field(..., description="Nombre de la oportunidad")
    contact_name: Optional[str] = Field(None, description="Nombre del contacto")
    partner_name: Optional[str] = Field(None, description="Nombre de la empresa")
    email_from: Optional[str] = Field(None, description="Email del contacto")
    phone: Optional[str] = Field(None, description="Teléfono")
    mobile: Optional[str] = Field(None, description="Móvil")
    website: Optional[str] = Field(None, description="Sitio web")
    function: Optional[str] = Field(None, description="Cargo/Posición")
    street: Optional[str] = Field(None, description="Dirección")
    city: Optional[str] = Field(None, description="Ciudad")
    zip: Optional[str] = Field(None, description="Código postal")
    country_id: Optional[int] = Field(None, description="ID del país")
    state_id: Optional[int] = Field(None, description="ID del estado")
    user_id: Optional[int] = Field(None, description="ID del vendedor")
    team_id: Optional[int] = Field(None, description="ID del equipo de ventas")
    stage_id: Optional[int] = Field(None, description="ID de la etapa")
    priority: Optional[str] = Field(None, description="Prioridad")
    expected_revenue: Optional[float] = Field(None, description="Ingresos esperados")
    probability: Optional[float] = Field(None, description="Probabilidad")
    description: Optional[str] = Field(None, description="Notas")
    type: str = Field(default="lead", description="Tipo: lead o opportunity")
    
    # Campos específicos del contexto universitario
    x_studio_programa_academico: Optional[int] = Field(None, description="ID del programa académico")
    x_studio_canal_de_contacto: Optional[str] = Field(None, description="Canal de contacto")
    x_studio_programa_de_interes: Optional[str] = Field(None, description="Programa de interés")
    progress: Optional[float] = Field(None, description="Progreso")
    manage_reason: Optional[str] = Field(None, description="Motivo de gestión")
    action_request_lead: Optional[str] = Field(None, description="Acción solicitada por lead")

class PartnerData(BaseModel):
    """Modelo para datos de Partner (res.partner)"""
    id: Optional[int] = None
    name: str = Field(..., description="Nombre del partner")
    display_name: Optional[str] = Field(None, description="Nombre para mostrar")
    email: Optional[str] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Teléfono")
    mobile: Optional[str] = Field(None, description="Móvil")
    website: Optional[str] = Field(None, description="Sitio web")
    is_company: bool = Field(default=False, description="Es una empresa")
    parent_id: Optional[int] = Field(None, description="ID del partner padre")
    street: Optional[str] = Field(None, description="Dirección")
    street2: Optional[str] = Field(None, description="Dirección 2")
    city: Optional[str] = Field(None, description="Ciudad")
    zip: Optional[str] = Field(None, description="Código postal")
    country_id: Optional[int] = Field(None, description="ID del país")
    state_id: Optional[int] = Field(None, description="ID del estado")
    function: Optional[str] = Field(None, description="Cargo/Posición")
    title: Optional[int] = Field(None, description="ID del título")
    category_id: Optional[List[int]] = Field(None, description="IDs de categorías")
    user_id: Optional[int] = Field(None, description="ID del vendedor responsable")
    vat: Optional[str] = Field(None, description="NIT/RUT")
    ref: Optional[str] = Field(None, description="Referencia interna")
    lang: Optional[str] = Field(None, description="Idioma")
    active: bool = Field(default=True, description="Activo")
    customer_rank: int = Field(default=0, description="Rango de cliente")
    supplier_rank: int = Field(default=0, description="Rango de proveedor")

class LeadSearchFilters(BaseModel):
    """Filtros para búsqueda de leads"""
    stage_id: Optional[int] = None
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    type: Optional[str] = None  # 'lead' or 'opportunity'
    priority: Optional[str] = None
    email_from: Optional[str] = None
    partner_name: Optional[str] = None
    contact_name: Optional[str] = None
    city: Optional[str] = None
    country_id: Optional[int] = None
    limit: int = Field(default=10, description="Límite de resultados")
    offset: int = Field(default=0, description="Desplazamiento")

class PartnerSearchFilters(BaseModel):
    """Filtros para búsqueda de partners"""
    is_company: Optional[bool] = None
    customer_rank: Optional[int] = None
    supplier_rank: Optional[int] = None
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    city: Optional[str] = None
    country_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    active: bool = Field(default=True, description="Solo activos")
    limit: int = Field(default=10, description="Límite de resultados")
    offset: int = Field(default=0, description="Desplazamiento")

class NaturalLanguageQuery(BaseModel):
    """Modelo para consultas en lenguaje natural"""
    query: str = Field(..., description="Consulta en lenguaje natural")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    max_tokens: int = Field(default=1000, description="Máximo tokens en la respuesta")

class OdooResponse(BaseModel):
    """Modelo para respuestas de Odoo"""
    success: bool
    data: Optional[Union[List[Dict[str, Any]], Dict[str, Any], int]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    count: Optional[int] = None

class AnthropicResponse(BaseModel):
    """Modelo para respuestas de Anthropic"""
    response: str
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

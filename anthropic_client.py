import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from models import NaturalLanguageQuery, AnthropicResponse

logger = logging.getLogger(__name__)

class AnthropicClient:
    """Cliente para procesar instrucciones en lenguaje natural usando Anthropic Claude"""
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY en variables de entorno o como parámetro")
            
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-haiku-20240307"  # Modelo más económico para la mayoría de casos
        
    def process_natural_language_query(self, query: NaturalLanguageQuery) -> AnthropicResponse:
        """
        Procesa una consulta en lenguaje natural y determina qué acción realizar en Odoo
        """
        try:
            system_prompt = self._get_system_prompt()
            user_message = self._format_user_message(query)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=query.max_tokens,
                temperature=0.1,  # Baja temperatura para respuestas más consistentes
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            return AnthropicResponse(
                response=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"Error procesando consulta con Anthropic: {str(e)}")
            return AnthropicResponse(
                response=f"Error procesando la consulta: {str(e)}"
            )
    
    def interpret_odoo_action(self, query: str, context: Optional[Dict[str, Any]] = None) -> AnthropicResponse:
        """
        Interpreta una consulta y sugiere qué acción realizar en Odoo CRM/Partners
        """
        try:
            system_prompt = self._get_odoo_action_system_prompt()
            
            user_message = f"""
            Consulta del usuario: {query}
            
            {f"Contexto adicional: {context}" if context else ""}
            
            Responde con un JSON que contenga:
            - action: la acción a realizar
            - model: el modelo de Odoo (crm.lead o res.partner)
            - parameters: parámetros necesarios para la acción
            - explanation: explicación de lo que se va a hacer
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            return AnthropicResponse(
                response=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"Error interpretando acción Odoo: {str(e)}")
            return AnthropicResponse(
                response=f"Error interpretando la acción: {str(e)}"
            )
    
    def generate_lead_summary(self, lead_data: Dict[str, Any]) -> AnthropicResponse:
        """
        Genera un resumen inteligente de un lead
        """
        try:
            system_prompt = """
            Eres un asistente especializado en CRM universitario. 
            Genera un resumen conciso y útil del lead proporcionado, 
            destacando información clave para el seguimiento comercial.
            """
            
            user_message = f"""
            Genera un resumen profesional del siguiente lead:
            
            {self._format_lead_data(lead_data)}
            
            El resumen debe incluir:
            - Información de contacto principal
            - Interés académico
            - Estado actual del proceso
            - Próximos pasos recomendados
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            return AnthropicResponse(
                response=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"Error generando resumen de lead: {str(e)}")
            return AnthropicResponse(
                response=f"Error generando resumen: {str(e)}"
            )
    
    def suggest_lead_actions(self, lead_data: Dict[str, Any]) -> AnthropicResponse:
        """
        Sugiere acciones a tomar basado en el estado del lead
        """
        try:
            system_prompt = """
            Eres un consultor de CRM universitario especializado en procesos de admisión.
            Analiza el lead y sugiere acciones específicas para mejorar la conversión.
            """
            
            user_message = f"""
            Basado en la información del siguiente lead, sugiere 3-5 acciones específicas:
            
            {self._format_lead_data(lead_data)}
            
            Las sugerencias deben ser:
            - Específicas y accionables
            - Apropiadas para el contexto universitario
            - Orientadas a mejorar la conversión
            - Considerando el canal y programa de interés
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.4,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            return AnthropicResponse(
                response=response.content[0].text,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"Error sugiriendo acciones: {str(e)}")
            return AnthropicResponse(
                response=f"Error generando sugerencias: {str(e)}"
            )
    
    def _get_system_prompt(self) -> str:
        """Prompt del sistema para consultas generales"""
        return """
        Eres un asistente especializado en CRM universitario y gestión de leads académicos.
        
        Ayudas a interpretar consultas sobre:
        - Leads y oportunidades de estudiantes potenciales
        - Partners (estudiantes, empresas, contactos)
        - Programas académicos y procesos de admisión
        - Seguimiento comercial y conversión de leads
        
        Contexto específico:
        - Trabajas con datos de UniversidadISep
        - Los leads pueden tener información sobre programas académicos de interés
        - Los canales de contacto incluyen web, redes sociales, eventos, referencias
        - El proceso incluye diferentes etapas desde prospecto hasta matriculado
        
        Responde de manera profesional, clara y orientada a la acción.
        """
    
    def _get_odoo_action_system_prompt(self) -> str:
        """Prompt específico para interpretar acciones de Odoo"""
        return """
        Eres un intérprete de consultas para un sistema CRM universitario basado en Odoo.
        
        Tienes acceso a estas acciones:
        
        PARA LEADS (crm.lead):
        - get_leads: buscar leads con filtros
        - create_lead: crear nuevo lead
        - update_lead: actualizar lead existente
        
        PARA PARTNERS (res.partner):
        - get_partners: buscar partners con filtros
        - create_partner: crear nuevo partner
        - update_partner: actualizar partner existente
        
        CAMPOS IMPORTANTES:
        - Leads: name, contact_name, email_from, phone, x_studio_programa_academico, 
                x_studio_canal_de_contacto, stage_id, user_id, team_id
        - Partners: name, email, phone, is_company, customer_rank, city, country_id
        
        Responde SIEMPRE con un JSON válido que contenga:
        {
            "action": "nombre_de_la_accion",
            "model": "crm.lead" | "res.partner",
            "parameters": {...},
            "explanation": "explicación clara de la acción"
        }
        """
    
    def _format_user_message(self, query: NaturalLanguageQuery) -> str:
        """Formatea el mensaje del usuario"""
        message = f"Consulta: {query.query}"
        
        if query.context:
            message += f"\n\nContexto adicional:\n"
            for key, value in query.context.items():
                message += f"- {key}: {value}\n"
        
        return message
    
    def _format_lead_data(self, lead_data: Dict[str, Any]) -> str:
        """Formatea datos del lead para el prompt"""
        formatted = ""
        
        # Información básica
        if lead_data.get('name'):
            formatted += f"Oportunidad: {lead_data['name']}\n"
        if lead_data.get('contact_name'):
            formatted += f"Contacto: {lead_data['contact_name']}\n"
        if lead_data.get('email_from'):
            formatted += f"Email: {lead_data['email_from']}\n"
        if lead_data.get('phone'):
            formatted += f"Teléfono: {lead_data['phone']}\n"
        
        # Información académica específica
        if lead_data.get('x_studio_programa_de_inters'):
            formatted += f"Programa de interés: {lead_data['x_studio_programa_de_inters']}\n"
        if lead_data.get('x_studio_canal_de_contacto'):
            formatted += f"Canal de contacto: {lead_data['x_studio_canal_de_contacto']}\n"
        if lead_data.get('progress'):
            formatted += f"Progreso: {lead_data['progress']}%\n"
        if lead_data.get('manage_reason'):
            formatted += f"Motivo de gestión: {lead_data['manage_reason']}\n"
        
        # Estado y asignación
        if lead_data.get('stage_id'):
            formatted += f"Etapa: {lead_data['stage_id']}\n"
        if lead_data.get('priority'):
            formatted += f"Prioridad: {lead_data['priority']}\n"
        if lead_data.get('expected_revenue'):
            formatted += f"Ingreso esperado: ${lead_data['expected_revenue']}\n"
        
        return formatted or "Sin datos de lead disponibles"
    
    def process_query(self, query_text: str) -> str:
        """Método simple para procesar consultas de texto (para pruebas)"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": query_text
                }]
            )
            return message.content[0].text if message.content else "Sin respuesta"
        except Exception as e:
            logger.error(f"Error procesando consulta simple: {e}")
            return f"Error: {str(e)}"

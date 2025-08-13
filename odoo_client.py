import xmlrpc.client
import ssl
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv
from models import LeadData, PartnerData, LeadSearchFilters, PartnerSearchFilters, OdooResponse

logger = logging.getLogger(__name__)

class OdooClient:
    """Cliente para conectar con Odoo 16 vía XML-RPC"""
    
    def __init__(self, url: str = None, db: str = None, username: str = None, password: str = None):
        # Cargar variables de entorno
        load_dotenv()
        
        # Verificar modo desarrollo
        self.dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
        self.mock_data = os.getenv('MOCK_ODOO_DATA', 'false').lower() == 'true'
        
        # Usar parámetros proporcionados o variables de entorno
        self.url = url or os.getenv('ODOO_URL')
        self.db = db or os.getenv('ODOO_DB')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.password = password or os.getenv('ODOO_PASSWORD')
        
        if not all([self.url, self.db, self.username, self.password]):
            raise ValueError("Faltan credenciales de Odoo. Verifica las variables de entorno o parámetros.")
        
        self.uid = None
        self.common = None
        self.models = None
        
        # Configurar SSL para evitar problemas de certificados
        self._setup_ssl_context()
        
        # Conectar (o simular en modo desarrollo)
        if self.dev_mode and self.mock_data:
            logger.info("🧪 Modo desarrollo activado - usando datos simulados")
            self.uid = 1  # Simular UID
        else:
            self._connect()
    
    def _setup_ssl_context(self):
        """Configurar contexto SSL para conexiones seguras"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
    def _connect(self):
        """Establecer conexión con Odoo"""
        try:
            # Conexión a common endpoint para autenticación
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Autenticarse y obtener UID
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                raise Exception("Error de autenticación con Odoo")
            
            # Conexión al endpoint de modelos
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            logger.info(f"Conectado a Odoo como usuario {self.username} (UID: {self.uid})")
            
        except Exception as e:
            logger.error(f"Error conectando a Odoo: {str(e)}")
            raise
    
    def _execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Ejecutar método en modelo de Odoo"""
        if kwargs is None:
            kwargs = {}
        
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
            return result
        except Exception as e:
            logger.error(f"Error ejecutando {method} en {model}: {str(e)}")
            raise
    
    # =================== MÉTODOS PARA CRM_LEAD ===================
    
    def get_leads(self, filters: LeadSearchFilters) -> OdooResponse:
        """Obtener leads del CRM"""
        try:
            # Construir dominio de búsqueda
            domain = []
            
            if filters.stage_id:
                domain.append(['stage_id', '=', filters.stage_id])
            if filters.user_id:
                domain.append(['user_id', '=', filters.user_id])
            if filters.team_id:
                domain.append(['team_id', '=', filters.team_id])
            if filters.type:
                domain.append(['type', '=', filters.type])
            if filters.priority:
                domain.append(['priority', '=', filters.priority])
            if filters.email_from:
                domain.append(['email_from', 'ilike', filters.email_from])
            if filters.partner_name:
                domain.append(['partner_name', 'ilike', filters.partner_name])
            if filters.contact_name:
                domain.append(['contact_name', 'ilike', filters.contact_name])
            if filters.city:
                domain.append(['city', 'ilike', filters.city])
            if filters.country_id:
                domain.append(['country_id', '=', filters.country_id])
            
            # Campos a obtener
            fields = [
                'id', 'name', 'contact_name', 'partner_name', 'email_from',
                'phone', 'mobile', 'website', 'function', 'street', 'city',
                'zip', 'country_id', 'state_id', 'user_id', 'team_id',
                'stage_id', 'priority', 'expected_revenue', 'probability',
                'description', 'type', 'create_date', 'write_date',
                'x_studio_programa_academico', 'x_studio_canal_de_contacto',
                'x_studio_programa_de_interes', 'progress', 'manage_reason',
                'action_request_lead'
            ]
            
            # Ejecutar búsqueda
            leads = self._execute_kw(
                'crm.lead', 'search_read',
                [domain],
                {
                    'fields': fields,
                    'limit': filters.limit,
                    'offset': filters.offset,
                    'order': 'create_date desc'
                }
            )
            
            # Contar total
            total_count = self._execute_kw('crm.lead', 'search_count', [domain])
            
            # Serializar objetos datetime antes de devolver
            serialized_leads = serialize_datetime_objects(leads)
            
            return OdooResponse(
                success=True,
                data=serialized_leads,
                count=total_count,
                message=f"Se encontraron {len(leads)} leads de {total_count} total"
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo leads: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message="Error al obtener leads"
            )
    
    def create_lead(self, lead_data: LeadData) -> OdooResponse:
        """Crear un nuevo lead"""
        try:
            # Convertir modelo a diccionario, excluyendo None y id
            data = lead_data.model_dump(exclude_none=True, exclude={'id'})
            
            # Crear lead
            lead_id = self._execute_kw('crm.lead', 'create', [data])
            
            # Obtener el lead creado
            created_lead = self._execute_kw(
                'crm.lead', 'read',
                [lead_id],
                {'fields': ['id', 'name', 'contact_name', 'partner_name', 'email_from', 'create_date', 'write_date']}
            )
            
            # Serializar objetos datetime
            serialized_data = serialize_datetime_objects(created_lead[0] if created_lead else {'id': lead_id})
            
            return OdooResponse(
                success=True,
                data=serialized_data,
                message=f"Lead creado exitosamente con ID {lead_id}"
            )
            
        except Exception as e:
            logger.error(f"Error creando lead: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message="Error al crear lead"
            )
    
    def update_lead(self, lead_id: int, lead_data: LeadData) -> OdooResponse:
        """Actualizar un lead existente"""
        try:
            # Verificar que el lead existe
            existing = self._execute_kw('crm.lead', 'search', [[['id', '=', lead_id]]])
            if not existing:
                return OdooResponse(
                    success=False,
                    error="Lead no encontrado",
                    message=f"No existe lead con ID {lead_id}"
                )
            
            # Convertir modelo a diccionario, excluyendo None e id
            data = lead_data.model_dump(exclude_none=True, exclude={'id'})
            
            # Actualizar lead
            result = self._execute_kw('crm.lead', 'write', [[lead_id], data])
            
            if result:
                # Obtener el lead actualizado
                updated_lead = self._execute_kw(
                    'crm.lead', 'read',
                    [lead_id],
                    {'fields': ['id', 'name', 'contact_name', 'partner_name', 'email_from', 'write_date', 'create_date']}
                )
                
                # Serializar objetos datetime
                serialized_data = serialize_datetime_objects(updated_lead[0] if updated_lead else {'id': lead_id})
                
                return OdooResponse(
                    success=True,
                    data=serialized_data,
                    message=f"Lead {lead_id} actualizado exitosamente"
                )
            else:
                return OdooResponse(
                    success=False,
                    error="Error en la actualización",
                    message=f"No se pudo actualizar el lead {lead_id}"
                )
                
        except Exception as e:
            logger.error(f"Error actualizando lead {lead_id}: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message=f"Error al actualizar lead {lead_id}"
            )
    
    # =================== MÉTODOS PARA RES_PARTNER ===================
    
    def get_partners(self, filters: PartnerSearchFilters) -> OdooResponse:
        """Obtener partners"""
        try:
            # Construir dominio de búsqueda
            domain = [['active', '=', filters.active]]
            
            if filters.is_company is not None:
                domain.append(['is_company', '=', filters.is_company])
            if filters.customer_rank is not None:
                domain.append(['customer_rank', '>=', filters.customer_rank])
            if filters.supplier_rank is not None:
                domain.append(['supplier_rank', '>=', filters.supplier_rank])
            if filters.user_id:
                domain.append(['user_id', '=', filters.user_id])
            if filters.category_id:
                domain.append(['category_id', 'in', [filters.category_id]])
            if filters.city:
                domain.append(['city', 'ilike', filters.city])
            if filters.country_id:
                domain.append(['country_id', '=', filters.country_id])
            if filters.name:
                domain.append(['name', 'ilike', filters.name])
            if filters.email:
                domain.append(['email', 'ilike', filters.email])
            
            # Campos a obtener
            fields = [
                'id', 'name', 'display_name', 'email', 'phone', 'mobile',
                'website', 'is_company', 'parent_id', 'street', 'street2',
                'city', 'zip', 'country_id', 'state_id', 'function', 'title',
                'category_id', 'user_id', 'vat', 'ref', 'lang', 'active',
                'customer_rank', 'supplier_rank', 'create_date', 'write_date'
            ]
            
            # Ejecutar búsqueda
            partners = self._execute_kw(
                'res.partner', 'search_read',
                [domain],
                {
                    'fields': fields,
                    'limit': filters.limit,
                    'offset': filters.offset,
                    'order': 'name asc'
                }
            )
            
            # Contar total
            total_count = self._execute_kw('res.partner', 'search_count', [domain])
            
            # Serializar objetos datetime antes de devolver
            serialized_partners = serialize_datetime_objects(partners)
            
            return OdooResponse(
                success=True,
                data=serialized_partners,
                count=total_count,
                message=f"Se encontraron {len(partners)} partners de {total_count} total"
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo partners: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message="Error al obtener partners"
            )
    
    def create_partner(self, partner_data: PartnerData) -> OdooResponse:
        """Crear un nuevo partner"""
        try:
            # Convertir modelo a diccionario, excluyendo None e id
            data = partner_data.model_dump(exclude_none=True, exclude={'id'})
            
            # Crear partner
            partner_id = self._execute_kw('res.partner', 'create', [data])
            
            # Obtener el partner creado
            created_partner = self._execute_kw(
                'res.partner', 'read',
                [partner_id],
                {'fields': ['id', 'name', 'display_name', 'email', 'is_company', 'create_date', 'write_date']}
            )
            
            # Serializar objetos datetime
            serialized_data = serialize_datetime_objects(created_partner[0] if created_partner else {'id': partner_id})
            
            return OdooResponse(
                success=True,
                data=serialized_data,
                message=f"Partner creado exitosamente con ID {partner_id}"
            )
            
        except Exception as e:
            logger.error(f"Error creando partner: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message="Error al crear partner"
            )
    
    def update_partner(self, partner_id: int, partner_data: PartnerData) -> OdooResponse:
        """Actualizar un partner existente"""
        try:
            # Verificar que el partner existe
            existing = self._execute_kw('res.partner', 'search', [[['id', '=', partner_id]]])
            if not existing:
                return OdooResponse(
                    success=False,
                    error="Partner no encontrado",
                    message=f"No existe partner con ID {partner_id}"
                )
            
            # Convertir modelo a diccionario, excluyendo None e id
            data = partner_data.model_dump(exclude_none=True, exclude={'id'})
            
            # Actualizar partner
            result = self._execute_kw('res.partner', 'write', [[partner_id], data])
            
            if result:
                # Obtener el partner actualizado
                updated_partner = self._execute_kw(
                    'res.partner', 'read',
                    [partner_id],
                    {'fields': ['id', 'name', 'display_name', 'email', 'write_date', 'create_date']}
                )
                
                # Serializar objetos datetime
                serialized_data = serialize_datetime_objects(updated_partner[0] if updated_partner else {'id': partner_id})
                
                return OdooResponse(
                    success=True,
                    data=serialized_data,
                    message=f"Partner {partner_id} actualizado exitosamente"
                )
            else:
                return OdooResponse(
                    success=False,
                    error="Error en la actualización",
                    message=f"No se pudo actualizar el partner {partner_id}"
                )
                
        except Exception as e:
            logger.error(f"Error actualizando partner {partner_id}: {str(e)}")
            return OdooResponse(
                success=False,
                error=str(e),
                message=f"Error al actualizar partner {partner_id}"
            )
    
    # =================== MÉTODOS AUXILIARES ===================
    
    def get_crm_stages(self) -> OdooResponse:
        """Obtener etapas del CRM"""
        try:
            stages = self._execute_kw(
                'crm.stage', 'search_read',
                [[]],
                {'fields': ['id', 'name', 'sequence', 'fold', 'team_id']}
            )
            
            # Serializar objetos datetime
            serialized_stages = serialize_datetime_objects(stages)
            
            return OdooResponse(
                success=True,
                data=serialized_stages,
                message=f"Se encontraron {len(stages)} etapas"
            )
        except Exception as e:
            return OdooResponse(success=False, error=str(e))
    
    def get_crm_teams(self) -> OdooResponse:
        """Obtener equipos de ventas"""
        try:
            teams = self._execute_kw(
                'crm.team', 'search_read',
                [[]],
                {'fields': ['id', 'name', 'user_id', 'member_ids']}
            )
            
            # Serializar objetos datetime
            serialized_teams = serialize_datetime_objects(teams)
            
            return OdooResponse(
                success=True,
                data=serialized_teams,
                message=f"Se encontraron {len(teams)} equipos"
            )
        except Exception as e:
            return OdooResponse(success=False, error=str(e))
    
    def get_countries(self) -> OdooResponse:
        """Obtener países"""
        try:
            countries = self._execute_kw(
                'res.country', 'search_read',
                [[]],
                {'fields': ['id', 'name', 'code'], 'limit': 250}
            )
            
            # Serializar objetos datetime
            serialized_countries = serialize_datetime_objects(countries)
            
            return OdooResponse(
                success=True,
                data=serialized_countries,
                message=f"Se encontraron {len(countries)} países"
            )
        except Exception as e:
            return OdooResponse(success=False, error=str(e))
    
    def test_connection(self) -> OdooResponse:
        """Probar conexión con Odoo"""
        try:
            # Verificar que podemos obtener info del usuario actual
            user_info = self._execute_kw('res.users', 'read', [self.uid], {'fields': ['name', 'login']})
            
            # Serializar objetos datetime
            serialized_info = serialize_datetime_objects(user_info[0] if user_info else {})
            
            return OdooResponse(
                success=True,
                data=serialized_info,
                message=f"Conexión exitosa con Odoo como {self.username}"
            )
        except Exception as e:
            return OdooResponse(
                success=False,
                error=str(e),
                message="Error probando conexión con Odoo"
            )

def serialize_datetime_objects(obj):
    """
    Convierte recursivamente objetos datetime en strings para serialización JSON
    """
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, dict):
        return {key: serialize_datetime_objects(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_objects(item) for item in obj]
    else:
        return obj

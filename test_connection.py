#!/usr/bin/env python3
"""
Script de diagnóstico para probar la conexión con Odoo
"""

import os
import xmlrpc.client
import ssl
from dotenv import load_dotenv

def test_odoo_connection():
    """Prueba diferentes configuraciones de conexión con Odoo"""
    load_dotenv()
    
    # Configuraciones a probar
    configs = [
        {
            'url': 'https://dev.odoo.universidadisep.com',
            'db': 'UniversidadISep',
            'username': 'iallamadas@universidadisep.com',
            'password': '&Ce!4bWNWe!EgFm%sWBn'
        },
        {
            'url': 'https://dev.odoo.universidadisep.com',
            'db': 'universidadisep',
            'username': 'iallamadas@universidadisep.com',
            'password': '&Ce!4bWNWe!EgFm%sWBn'
        },
        {
            'url': 'https://dev.odoo.universidadisep.com',
            'db': 'odoo',
            'username': 'iallamadas@universidadisep.com',
            'password': '&Ce!4bWNWe!EgFm%sWBn'
        }
    ]
    
    # Configurar SSL
    ssl._create_default_https_context = ssl._create_unverified_context
    
    print("🔧 DIAGNÓSTICO DE CONEXIÓN ODOO")
    print("=" * 50)
    
    for i, config in enumerate(configs, 1):
        print(f"\n📋 Configuración {i}:")
        print(f"   URL: {config['url']}")
        print(f"   DB: {config['db']}")
        print(f"   Usuario: {config['username']}")
        
        try:
            # Probar conexión básica
            common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
            version_info = common.version()
            print(f"   ✅ Conexión al servidor: OK")
            print(f"   ℹ️  Versión Odoo: {version_info['server_version']}")
            
            # Probar autenticación
            uid = common.authenticate(config['db'], config['username'], config['password'], {})
            
            if uid:
                print(f"   ✅ Autenticación: EXITOSA (UID: {uid})")
                
                # Probar acceso a modelos
                models = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/object")
                
                # Verificar acceso a res.users
                user_info = models.execute_kw(
                    config['db'], uid, config['password'],
                    'res.users', 'read', [uid], {'fields': ['name', 'login']}
                )
                print(f"   ✅ Acceso a modelos: OK")
                print(f"   👤 Usuario: {user_info[0]['name']} ({user_info[0]['login']})")
                
                # Verificar acceso a CRM
                try:
                    crm_count = models.execute_kw(
                        config['db'], uid, config['password'],
                        'crm.lead', 'search_count', [[]]
                    )
                    print(f"   ✅ Acceso CRM: OK ({crm_count} leads encontrados)")
                except Exception as e:
                    print(f"   ❌ Acceso CRM: {str(e)}")
                
                # Verificar acceso a Partners
                try:
                    partner_count = models.execute_kw(
                        config['db'], uid, config['password'],
                        'res.partner', 'search_count', [[]]
                    )
                    print(f"   ✅ Acceso Partners: OK ({partner_count} partners encontrados)")
                except Exception as e:
                    print(f"   ❌ Acceso Partners: {str(e)}")
                
                print(f"   🎉 CONFIGURACIÓN {i} FUNCIONA COMPLETAMENTE!")
                return config
                
            else:
                print(f"   ❌ Autenticación: FALLIDA")
                
        except xmlrpc.client.Fault as e:
            print(f"   ❌ Error Odoo: {e}")
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
    
    print(f"\n❌ Ninguna configuración funcionó completamente")
    return None

if __name__ == "__main__":
    working_config = test_odoo_connection()
    
    if working_config:
        print(f"\n🔧 CONFIGURACIÓN RECOMENDADA:")
        print(f"ODOO_URL={working_config['url']}")
        print(f"ODOO_DB={working_config['db']}")
        print(f"ODOO_USERNAME={working_config['username']}")
        print(f"ODOO_PASSWORD={working_config['password']}")

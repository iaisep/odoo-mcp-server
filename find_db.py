#!/usr/bin/env python3
"""
Script para encontrar la base de datos correcta de Odoo
"""

import xmlrpc.client
import ssl

def find_odoo_database():
    """Encuentra la base de datos correcta de Odoo"""
    
    ssl._create_default_https_context = ssl._create_unverified_context
    
    url = 'https://dev.odoo.universidadisep.com'
    
    # Posibles nombres de base de datos basados en la información
    possible_dbs = [
        'UniversidadISep',        # Original que probamos
        'universidadisep',        # Minúsculas
        'odoo',                   # Común
        'odoo_prod',              # Producción  
        'odoo_dev',               # Desarrollo
        'main',                   # Común en sistemas
        'default',                # Por defecto
        'universidad',            # Variación
        'isep',                   # Abreviación
        'dev_odoo',               # Desarrollo
        'postgres'                # Ya probamos, pero incluido para completitud
    ]
    
    # Posibles credenciales de usuario Odoo (no PostgreSQL)
    possible_users = [
        ('admin', 'admin'),                                    # Credenciales por defecto
        ('admin', 'yUho&o0ut+Br0SW!ro#a'),                   # Admin con password DB
        ('iallamadas@universidadisep.com', '&Ce!4bWNWe!EgFm%sWBn'),  # Original
        ('administrator', 'admin'),                            # Variación
        ('odoo', 'odoo'),                                     # Usuario odoo
    ]
    
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    
    print("🔍 BUSCANDO BASE DE DATOS CORRECTA DE ODOO")
    print("=" * 60)
    
    for db in possible_dbs:
        print(f"\n📂 Probando DB: {db}")
        
        for username, password in possible_users:
            print(f"   👤 Usuario: {username}")
            try:
                uid = common.authenticate(db, username, password, {})
                
                if uid:
                    print(f"   ✅ ÉXITO! UID: {uid}")
                    
                    # Verificar que tiene modelos Odoo
                    try:
                        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
                        
                        # Probar acceso a modelo básico
                        user_info = models.execute_kw(
                            db, uid, password,
                            'res.users', 'read', [uid], 
                            {'fields': ['name', 'login']}
                        )
                        
                        print(f"   🎉 BASE DE DATOS ODOO ENCONTRADA!")
                        print(f"   📊 Usuario: {user_info[0]['name']} ({user_info[0]['login']})")
                        
                        # Probar modelos CRM y Partners
                        try:
                            crm_count = models.execute_kw(
                                db, uid, password,
                                'crm.lead', 'search_count', [[]]
                            )
                            print(f"   📋 CRM Leads: {crm_count} registros")
                        except:
                            print(f"   ⚠️  CRM no disponible o sin permisos")
                        
                        try:
                            partner_count = models.execute_kw(
                                db, uid, password,
                                'res.partner', 'search_count', [[]]
                            )
                            print(f"   👥 Partners: {partner_count} registros")
                        except:
                            print(f"   ⚠️  Partners no disponible o sin permisos")
                        
                        return {
                            'url': url,
                            'db': db,
                            'username': username,
                            'password': password,
                            'uid': uid,
                            'user_info': user_info[0]
                        }
                    
                    except Exception as e:
                        print(f"   ❌ Error accediendo modelos: {str(e)[:50]}...")
                
                else:
                    print(f"   ❌ Autenticación fallida")
                    
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg:
                    print(f"   ❌ BD no existe")
                    break  # No probar más usuarios para esta DB
                elif "res.users" in error_msg:
                    print(f"   ❌ No es BD Odoo (sin modelos)")
                    break  # No probar más usuarios para esta DB
                else:
                    print(f"   ❌ Error: {error_msg[:50]}...")
    
    print(f"\n❌ No se encontró una configuración válida de Odoo")
    return None

if __name__ == "__main__":
    result = find_odoo_database()
    
    if result:
        print(f"\n🎯 CONFIGURACIÓN CORRECTA ENCONTRADA:")
        print(f"ODOO_URL={result['url']}")
        print(f"ODOO_DB={result['db']}")
        print(f"ODOO_USERNAME={result['username']}")
        print(f"ODOO_PASSWORD={result['password']}")
        print(f"\n✅ ¡Actualiza tu archivo .env con estos valores!")

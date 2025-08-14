#!/usr/bin/env python3
"""
Script para probar diferentes variaciones de credenciales
"""

import xmlrpc.client
import ssl

def test_user_variations():
    """Prueba diferentes variaciones del usuario"""
    
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Configuración base
    url = 'https://dev.odoo.universidadisep.com'
    db = 'UniversidadISep'
    password = '&Ce!4bWNWe!EgFm%sWBn'
    
    # Variaciones de usuario a probar
    user_variations = [
        'iallamadas@universidadisep.com',
        'admin',
        'administrator',
        'iallamadas',
        'universidadisep@gmail.com',
        'admin@universidadisep.com',
    ]
    
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    
    print("🔧 PROBANDO VARIACIONES DE USUARIO")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"DB: {db}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    for user in user_variations:
        print(f"👤 Probando usuario: {user}")
        try:
            uid = common.authenticate(db, user, password, {})
            if uid:
                print(f"   ✅ ÉXITO! UID: {uid}")
                
                # Obtener información del usuario
                models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
                user_info = models.execute_kw(
                    db, uid, password,
                    'res.users', 'read', [uid], {'fields': ['name', 'login', 'email']}
                )
                print(f"   👤 Nombre: {user_info[0].get('name', 'N/A')}")
                print(f"   📧 Email: {user_info[0].get('email', 'N/A')}")
                print(f"   🔑 Login: {user_info[0].get('login', 'N/A')}")
                return {'username': user, 'uid': uid, 'user_info': user_info[0]}
            else:
                print(f"   ❌ Autenticación fallida")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}...")
        print()
    
    print("❌ Ninguna variación de usuario funcionó")
    return None

if __name__ == "__main__":
    result = test_user_variations()
    if result:
        print(f"🎉 CREDENCIALES CORRECTAS ENCONTRADAS:")
        print(f"Username: {result['username']}")
        print(f"UID: {result['uid']}")
        print(f"Nombre completo: {result['user_info']['name']}")

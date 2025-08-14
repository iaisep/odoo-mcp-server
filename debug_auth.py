#!/usr/bin/env python3

import xmlrpc.client
import ssl
import os
from dotenv import load_dotenv

load_dotenv()
ssl._create_default_https_context = ssl._create_unverified_context

url = os.getenv('ODOO_URL')
db = os.getenv('ODOO_DB') 
username = os.getenv('ODOO_USERNAME')
password = os.getenv('ODOO_PASSWORD')

print('🔧 Configuración:')
print(f'   URL: {url}')
print(f'   DB: {db}')
print(f'   Usuario: {username}')
print(f'   Password: {password[:5]}***{password[-5:]}')
print()

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    version = common.version()
    print(f'✅ Servidor conectado: {version["server_version"]}')
    
    uid = common.authenticate(db, username, password, {})
    print(f'🔑 Resultado autenticación: {uid}')
    
    if uid:
        print(f'✅ AUTENTICACIÓN EXITOSA - UID: {uid}')
        
        # Probar acceso a modelos
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        user_info = models.execute_kw(
            db, uid, password,
            'res.users', 'read', [uid], 
            {'fields': ['name', 'login', 'email']}
        )
        print(f'👤 Usuario: {user_info[0]["name"]} ({user_info[0]["login"]})')
        
    else:
        print(f'❌ AUTENTICACIÓN FALLIDA - UID es {uid}')
        print('   Posibles causas:')
        print('   - Usuario no existe')  
        print('   - Contraseña incorrecta')
        print('   - Usuario desactivado')
        
except Exception as e:
    print(f'❌ Error: {e}')

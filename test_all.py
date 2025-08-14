#!/usr/bin/env python3
"""
Script para probar las funcionalidades del servidor MCP
"""

from odoo_client import OdooClient
from anthropic_client import AnthropicClient
import os
from dotenv import load_dotenv

def test_all_components():
    """Probar todas las funcionalidades del servidor MCP"""
    load_dotenv()
    
    print("🔧 PRUEBAS DEL SERVIDOR MCP")
    print("=" * 50)
    
    # 1. Probar conexión Odoo
    print("\n1️⃣ PROBANDO CONEXIÓN ODOO...")
    try:
        odoo = OdooClient()
        print(f"✅ Odoo conectado - UID: {odoo.uid}")
    except Exception as e:
        print(f"❌ Error Odoo: {e}")
        return
    
    # 2. Probar conexión Anthropic
    print("\n2️⃣ PROBANDO CONEXIÓN ANTHROPIC...")
    try:
        anthropic_client = AnthropicClient()
        test_query = "¿Cómo estás?"
        response = anthropic_client.process_query(test_query)
        print(f"✅ Anthropic funcional: {response[:50]}...")
    except Exception as e:
        print(f"❌ Error Anthropic: {e}")
    
    # 3. Probar acceso a modelos Odoo básicos
    print("\n3️⃣ PROBANDO ACCESO A MODELOS ODOO...")
    try:
        # Probar res.users
        users = odoo._execute_kw('res.users', 'search_read', [[]], {'limit': 3, 'fields': ['name', 'login']})
        print(f"✅ Usuarios encontrados: {len(users)}")
        for user in users:
            print(f"   • {user.get('name')} ({user.get('login')})")
    except Exception as e:
        print(f"❌ Error usuarios: {e}")
    
    try:
        # Probar res.partner
        partners = odoo._execute_kw('res.partner', 'search_read', [[]], {'limit': 3, 'fields': ['name', 'email']})
        print(f"✅ Partners encontrados: {len(partners)}")
        for partner in partners:
            print(f"   • {partner.get('name')} ({partner.get('email')})")
    except Exception as e:
        print(f"❌ Error partners: {e}")
    
    try:
        # Probar crm.lead
        leads = odoo._execute_kw('crm.lead', 'search_read', [[]], {'limit': 3, 'fields': ['name', 'email_from', 'stage_id']})
        print(f"✅ CRM Leads encontrados: {len(leads)}")
        for lead in leads:
            print(f"   • {lead.get('name')} ({lead.get('email_from')})")
    except Exception as e:
        print(f"❌ Error CRM: {e}")

if __name__ == "__main__":
    test_all_components()

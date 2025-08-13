#!/usr/bin/env python3
"""
Monitor de Coolify - Verifica el estado del deployment periódicamente
"""

import requests
import time
import json
from datetime import datetime

def check_coolify_status(url):
    """Verificar estado del deployment en Coolify"""
    try:
        # Health check
        health_url = f"{url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=10)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[{timestamp}] ✅ HEALTHY - Odoo: {data.get('odoo_connected')}, Anthropic: {data.get('anthropic_available')}")
            return True
        elif response.status_code == 503:
            print(f"[{timestamp}] ❌ 503 - no available server (app not running)")
            return False
        else:
            print(f"[{timestamp}] ⚠️  Status: {response.status_code} - {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ Connection Error - Can't reach Coolify")
        return False
    except Exception as e:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ Error: {e}")
        return False

def monitor_coolify(url, interval=30):
    """Monitorear Coolify cada X segundos"""
    print(f"🔍 Monitoreando Coolify: {url}")
    print(f"⏱️  Verificando cada {interval} segundos")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            check_coolify_status(url)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")

if __name__ == "__main__":
    # Tu URL de Coolify
    coolify_url = "https://dev2.odoo.universidadisep.com"
    
    print("🚀 Monitor de Coolify para servidor MCP de Odoo\n")
    
    # Verificación inicial
    print("📡 Verificación inicial:")
    is_healthy = check_coolify_status(coolify_url)
    
    if is_healthy:
        print("\n✅ ¡El servidor está funcionando!")
        print("   Puedes usar la URL para conectar n8n")
    else:
        print("\n❌ El servidor no está respondiendo correctamente")
        print("   Revisa el deployment en Coolify")
    
    # Preguntar si quiere monitoreo continuo
    monitor = input("\n🔍 ¿Quieres monitoreo continuo? (y/n): ").lower().strip()
    if monitor in ['y', 'yes', 's', 'si']:
        interval = input("⏱️  Intervalo en segundos (default: 30): ").strip()
        interval = int(interval) if interval.isdigit() else 30
        monitor_coolify(coolify_url, interval)

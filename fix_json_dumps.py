#!/usr/bin/env python3
"""
Script para reemplazar todas las ocurrencias de json.dumps(result.model_dump() con safe_json_dumps
"""
import re

# Leer el archivo
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar todas las ocurrencias
# Patrón: return json.dumps(result.model_dump(), ... 
pattern = r'return json\.dumps\(result\.model_dump\(\)'
replacement = r'return safe_json_dumps(result.model_dump()'

new_content = re.sub(pattern, replacement, content)

# Escribir el archivo actualizado
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Reemplazos completados")
print(f"Total de reemplazos: {len(re.findall(pattern, content))}")

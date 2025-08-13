# Setup Virtual Environment
python -m venv venv

# Activate Virtual Environment (Windows)
.\venv\Scripts\activate

# Install Dependencies  
pip install -r requirements.txt

# Configure Environment
# Edit .env file with your credentials

# Test Odoo Connection
python -c "from odoo_client import OdooClient; client = OdooClient(); print('Connection test:', client.authenticate())"

# Run MCP Server
python main.py

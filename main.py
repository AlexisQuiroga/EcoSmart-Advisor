"""
EcoSmart Advisor
Una aplicación inteligente que asesora a los usuarios sobre qué sistema 
de energía renovable les conviene instalar según su ubicación y condiciones.
"""
import os
from flask import Flask, render_template

from ecosmart_advisor.app import create_app

if __name__ == "__main__":
    app = create_app()
    # Using 0.0.0.0 to make it accessible outside localhost
    # Use PORT environment variable if available (for Replit deployment)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
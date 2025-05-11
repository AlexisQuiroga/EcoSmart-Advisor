import os

bind = f"0.0.0.0:{int(os.environ.get('PORT', 8080))}"
workers = 2
timeout = 120
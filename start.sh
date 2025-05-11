#!/bin/bash

# Ejecutar con Gunicorn para producción
gunicorn --config gunicorn_config.py app:app
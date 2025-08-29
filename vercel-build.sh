#!/bin/bash
# Script de build personalizado para Vercel

echo "🚀 Iniciando build personalizado para Vercel..."

# Verificar que estamos usando el archivo correcto de dependencias
if [ -f "requirements-vercel.txt" ]; then
    echo "✅ Instalando dependencias desde requirements-vercel.txt"
    pip install -r requirements-vercel.txt
else
    echo "❌ requirements-vercel.txt no encontrado"
    exit 1
fi

echo "✅ Build completado exitosamente"

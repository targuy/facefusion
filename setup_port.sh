#!/bin/bash
# Script pour configurer manuellement le port forwarding dans Codespaces

echo "🔧 Configuration du port forwarding pour Codespaces..."

# Vérifier si on est dans Codespaces
if [[ "$CODESPACES" != "true" ]]; then
    echo "❌ Ce script ne fonctionne que dans GitHub Codespaces"
    exit 1
fi

echo "📡 Configuration du port 7860 pour FaceFusion..."

# Utiliser gh CLI pour configurer le port forwarding si disponible
if command -v gh &> /dev/null; then
    echo "🔧 Configuration via GitHub CLI..."
    gh codespace ports forward 7860:7860 --visibility public 2>/dev/null || echo "⚠️ Impossible de configurer automatiquement via gh CLI"
fi

echo ""
echo "📋 Instructions manuelles :"
echo "1. Dans VS Code, allez dans l'onglet 'Ports' (en bas de l'écran)"
echo "2. Cliquez sur 'Add Port' ou le bouton '+'"
echo "3. Tapez '7860' et appuyez sur Entrée"
echo "4. Clic droit sur le port 7860 → 'Port Visibility' → 'Public'"
echo "5. Cliquez sur l'icône '🌐' pour ouvrir dans le navigateur"
echo ""
echo "🚀 Maintenant lancez FaceFusion avec : ./launch_web.sh"
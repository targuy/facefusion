#!/bin/bash
# Script pour lancer FaceFusion avec l'interface web dans Codespaces

echo "🚀 Lancement de FaceFusion avec interface web..."

# Activer l'environnement virtuel
source .venv/bin/activate

# Vérifier si on est dans Codespaces
if [[ "$CODESPACES" == "true" ]]; then
    echo "📱 Détection de GitHub Codespaces"
    echo "🌐 FaceFusion va créer un lien public Gradio automatiquement"
    echo "🔗 Le lien sera affiché dans la console au démarrage"
    echo "💡 Alternative: Utilisez l'onglet 'Ports' de VS Code pour le port 7860"
    echo ""
fi

# Lancer FaceFusion avec interface web
echo "🎭 Démarrage de l'interface FaceFusion..."
echo "⏳ Chargement des modèles (peut prendre quelques minutes)..."
python facefusion.py run

echo "✅ FaceFusion terminé"
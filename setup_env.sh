#!/bin/bash
# Script pour configurer l'environnement FaceFusion

echo "🚀 Configuration de l'environnement FaceFusion..."

# Activer l'environnement virtuel
source .venv/bin/activate

echo "✅ Environnement virtuel activé"
echo "📦 Packages installés :"
echo "   - NumPy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "   - OpenCV: $(python -c 'import cv2; print(cv2.__version__)')"
echo "   - ONNX: $(python -c 'import onnx; print(onnx.__version__)')"
echo "   - ONNX Runtime: $(python -c 'import onnxruntime; print(onnxruntime.__version__)')"

echo ""
echo "🎭 FaceFusion est prêt !"
echo "📚 Exemples de commandes :"
echo "   python facefusion.py --help"
echo "   python facefusion.py repo-list"
echo "   python facefusion.py repo-add --person 'Marie' --face-paths face1.jpg face2.jpg"
echo ""
echo "🔧 Pour désactiver l'environnement : deactivate"
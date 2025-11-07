# FaceFusion dans GitHub Codespaces

## 🚀 Lancement rapide

### Interface Web (recommandé)
```bash
./launch_web.sh
```

Ou manuellement :
```bash
source .venv/bin/activate
python facefusion.py run
```

### CLI seulement
```bash
source .venv/bin/activate
python facefusion.py --help
```

## 🌐 Accès à l'interface web - RÉSOLU ✅

### Option 1: Lien public Gradio (recommandé)
- ✅ **Utilisez le lien affiché dans la console** au démarrage
- 🌐 Format : `https://XXXXX.gradio.live`
- ⚠️ Nouveau lien généré à chaque redémarrage

### Option 2: Port forwarding Codespaces
1. **Après lancement** :
   - Regardez l'onglet **"Ports"** dans VS Code
   - Le port `7860` devrait apparaître automatiquement
   - Clic droit → "Port Visibility" → "Public"
   - Cliquez sur l'icône "🌐" pour ouvrir dans le navigateur

2. **Configuration manuelle** :
   - Allez dans l'onglet "Ports" (`Ctrl+Shift+P` puis "Ports: Focus on Ports Panel")
   - Ajoutez le port `7860` 
   - Cliquez sur "Open in Browser"

## 🛠️ Configuration Codespaces

Les modifications suivantes ont été appliquées pour optimiser FaceFusion dans Codespaces :

- **Server binding** : `0.0.0.0` (écoute sur toutes les interfaces)
- **Port fixe** : `7860` (pour un forwarding prévisible)
- **Auto-browser** : désactivé (ne fonctionne pas dans Codespaces)
- **Share public** : désactivé (utilise le forwarding de Codespaces)

## 📝 Commandes utiles

### Repository
```bash
# Lister les personnes
python facefusion.py repo-list

# Ajouter une personne
python facefusion.py repo-add --person "Marie" --face-paths image1.jpg image2.jpg

# Utiliser une personne du repository
python facefusion.py repo-execute --person "Marie" --target video.mp4 --output result.mp4
```

### Processing direct
```bash
# Face swap simple
python facefusion.py headless-run --source face.jpg --target video.mp4 --output result.mp4

# Avec processeurs multiples
python facefusion.py headless-run --source face.jpg --target video.mp4 --output result.mp4 --processors face_swapper face_enhancer
```

## 🔧 Dépannage

### Port 7860 non accessible
1. Vérifiez que FaceFusion est en cours d'exécution
2. Dans VS Code : `View` → `Open View...` → `Ports`
3. Si le port 7860 n'apparaît pas, ajoutez-le manuellement
4. Assurez-vous que la visibilité est "Public"

### Interface lente
- Les Codespaces ont des ressources limitées
- Utilisez des images/vidéos plus petites pour les tests
- Préférez `headless-run` pour les traitements lourds

### Problèmes de dépendances
```bash
# Réinstaller les dépendances
source .venv/bin/activate
pip install -r requirements.txt
```
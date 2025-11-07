# Analyse: Spécifications vs Implémentation Actuelle

## ✅ DÉJÀ IMPLÉMENTÉ

### 3.1 Création de Personne
- ✅ `create_or_update_person()` existe dans manager.py
- ✅ Merge automatique si personne existe
- ✅ Vérification unicité noms (normalized_name)
- ✅ Extraction orientation 3D
- ✅ Calcul qualité multi-critères
- ✅ Filtrage par quality_threshold
- ✅ Détection orientation overlap

### 3.2 Visualisation Repository (Partiel)
- ✅ Gallery Gradio avec miniatures
- ✅ Liste personnes avec face_count
- ✅ Bouton Select
- ✅ Bouton Delete
- ✅ Coverage statistics (P1.4 complété)
- ❌ Pas de "Check Availability" pour nom
- ❌ Pas de "[Add Faces]" par personne (utilise formulaire général)
- ❌ Pas de "[View 3D Map]" individuel

### 3.3 Preview Modal
- ❌ MANQUANT COMPLÈTEMENT
- ❌ Pas de modal confirmation avant ajout
- ❌ Pas d'affichage détections face par face
- ❌ Pas d'affichage orientation/qualité avant confirmation
- ❌ Pas de résumé des overlaps/skips

### 3.4 Couverture 3D Visualization
- ❌ MANQUANT COMPLÈTEMENT
- ❌ Pas de sphère 3D interactive
- ❌ Pas de visualisation zones couvertes/manquantes
- ❌ Pas de suggestions d'angles à ajouter
- ✅ Coverage stats textuels existent (P1.4)

### 3.5 Swap Preview avec Test Faces
- ❌ MANQUANT COMPLÈTEMENT
- ⚠️ Fonctions preview existent dans manager.py mais pas d'UI
- ❌ Pas de modal preview swap
- ❌ Pas de rotation 3D interactive

### 3.6 Gestion de State
- ✅ Variables repository_mode, repository_person_id, etc.
- ✅ repository_helper.get_effective_source_paths()
- ✅ Priorité repository > upload direct
- ✅ Clear mode opposé lors switch

### 3.7 Intégration Face Selector
- ⚠️ RepositorySelector existe mais pas intégré à face_selector.py
- ❌ Pas de sélection automatique basée orientation target

### 4.1 Structure PersonEntry
- ✅ face_metadata avec pose
- ✅ face_metadata avec quality
- ✅ coverage_stats (ajouté P1.4)
- ⚠️ zone pas stocké dans face_metadata (calculé dynamiquement)
- ⚠️ metadata.description/tags pas implémenté

### 4.2 Repository JSON Structure
- ✅ Structure de base
- ✅ persons dict
- ❌ settings.default_quality_threshold pas dans JSON (hardcodé)

---

## 📋 PRIORITÉS D'IMPLÉMENTATION

### P2.1 - Preview Modal (CRITIQUE - spec 3.3)
**Complexité**: Haute  
**Impact**: Très élevé (transparence utilisateur)  
**Status**: À implémenter

**Ce qui manque**:
- Modal Gradio avec preview avant confirmation
- Affichage détections + métriques par face
- Résumé overlaps/replacements
- Boutons Cancel/Confirm

### P2.2 - Progress Feedback (MOYEN - amélioration UX)
**Complexité**: Moyenne  
**Impact**: Moyen (confort utilisateur)  
**Status**: À implémenter

**Ce qui manque**:
- gradio.Progress integration
- Messages temps réel "Processing 1/5..."
- Callbacks dans manager

### P2.4 - Metadata Overlays (MOYEN - amélioration visuelle)
**Complexité**: Moyenne  
**Impact**: Moyen (facilite compréhension)  
**Status**: À implémenter

**Ce qui manque**:
- Badges qualité sur thumbnails
- Indicateurs orientation (flèches)
- Warnings visuels (⚠️)

### P3.1 - 3D Visualization (NICE-TO-HAVE - spec 3.4)
**Complexité**: Très haute  
**Impact**: Élevé mais optionnel  
**Status**: À implémenter

**Ce qui manque**:
- Sphère 3D plotly/matplotlib
- Visualisation zones couvertes/manquantes
- Suggestions angles manquants
- Modal "[View 3D Map]"

---

## 🎯 PLAN D'ACTION

### Phase 1: P2.1 Preview Modal (2-3h)
1. Créer Modal component avec gradio.Modal
2. Appeler preview_face_import() pour chaque fichier
3. Afficher grid avec détections + métriques
4. Implémenter logique Cancel/Confirm
5. Intégrer dans workflow add_person

### Phase 2: P2.2 Progress Feedback (1-2h)
1. Ajouter param progress: gradio.Progress
2. Wrapper manager functions avec progress updates
3. Afficher "Processing X/Y", "Detecting...", etc.
4. Tester avec uploads lents

### Phase 3: P2.4 Metadata Overlays (2-3h)
1. Créer fonction annotate_thumbnail() avec PIL
2. Ajouter badges qualité (⭐ x5)
3. Ajouter flèches orientation (→↗↑↖)
4. Ajouter warnings (⚠️ si overlap/low quality)
5. Intégrer dans gallery refresh

### Phase 4: P3.1 3D Visualization (4-6h)
1. Créer fonction generate_3d_sphere() avec plotly
2. Convertir orientations (pitch/yaw) → coordonnées sphériques
3. Plot points avec couleur = qualité
4. Ajouter zones manquantes en rouge
5. Créer modal "[View 3D Map]"
6. Ajouter tab séparé dans UI

---

## ⚠️ GAPS SPÉCIFICATIONS vs CODE

### Specs mentionnent mais pas implémenté:
1. **Check Availability** pour noms (ligne 206 spec)
2. **[Add Faces]** par personne (ligne 218 spec)
3. **Test Faces swap preview** (section 3.5)
4. **Auto-rotate preview** (ligne 337 spec)
5. **Export frames/report** (lignes 344, 290 spec)
6. **metadata.description/tags** (ligne 416 spec)
7. **settings dans JSON** (ligne 438 spec)

### Priorité:
- **P0**: Preview Modal (3.3) - Critique pour UX
- **P1**: 3D Viz (3.4) - Forte valeur mais complexe
- **P2**: Progress feedback (amélioration)
- **P2**: Metadata overlays (amélioration)
- **P3**: Features additionnelles (Check Availability, Export, etc.)

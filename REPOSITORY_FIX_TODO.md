# REPOSITORY FIX - TODO LIST & PROGRESS TRACKER

**Créé:** 2025-10-31  
**Objectif:** Corriger tous les problèmes identifiés du système repository  
**Référence:** REPOSITORY_SPECIFICATIONS.md

---

## 📊 PROGRESSION GLOBALE

- **Total tâches:** 23
- **Complétées:** 4 ✅ (P0.1, P0.2, P0.3, P1.1)
- **En cours:** 0 🔄
- **À faire:** 19 ⏳
- **Bloquées:** 0 ⛔

**Progression:** ████░░░░░░░░░░░░░░░░ 17% (4/23)

**P0 (Bloquants):** 3/3 complétés ✅ **TOUS LES BLOQUANTS RÉSOLUS !**  
**P1 (Important):** 1/4 complétés

---

## 🎯 PRIORITÉ 0 - BLOQUANTS (Must Fix)

### P0.1 - Unicité des noms de personnes ✅
**Fichier:** `facefusion_repository/manager.py`  
**Problème:** Doublons de noms possibles  
**Solution:**
- Ajouter `normalized_name` dans PersonEntry
- Vérifier unicité dans `create_person()`
- Ajouter `get_person_by_normalized_name()`
- Retourner erreur explicite si doublon

**Checklist:**
- [x] Ajouter champ `normalized_name` dans types.py
- [x] Modifier `create_person()` pour vérifier unicité
- [x] Ajouter fonction `_normalize_name(name: str) -> str`
- [x] Ajouter fonction `get_person_by_normalized_name()`
- [x] UI affiche erreur si doublon
- [ ] Tester: création doublon → erreur (besoin de lancer l'app)
- [ ] Tester: case différente détectée comme doublon (besoin de lancer l'app)

**Temps estimé:** 30 min  
**Temps réel:** 20 min  
**Statut:** ✅ Complété (tests manuels à faire)

---

### P0.2 - Séparation variables state repository vs upload ✅
**Fichiers:**
- `facefusion/types.py`
- `facefusion/uis/components/repository.py`
- `facefusion/repository_helper.py` (nouveau)

**Problème:** Conflit entre `source_paths` repository et upload direct

**Solution:**
```python
# Nouvelles variables state
'repository_mode': bool
'repository_person_id': str  
'repository_person_name': str
'repository_source_faces': List[str]
'source_paths': List[str]  # Legacy (direct upload)
```

**Checklist:**
- [x] Ajouter nouvelles clés dans types.py (StateKey + State TypedDict)
- [x] Modifier `repository.py::update_selected_person()` pour utiliser variables séparées
- [x] Créer `repository_helper.py` avec `get_effective_source_faces()`
- [x] Ajouter helpers: `is_repository_mode_active()`, `get_repository_person_name()`, `get_repository_person_id()`
- [ ] Modifier face_selector.py pour utiliser get_effective_source_faces()
- [ ] Tester: sélection repository ne casse pas upload direct (besoin app)
- [ ] Tester: upload direct fonctionne si pas de repository (besoin app)
- [ ] Tester: switch entre modes fonctionne (besoin app)

**Temps estimé:** 1h  
**Temps réel:** 25 min (partie backend)  
**Statut:** ✅ Complété (intégration face_selector reste à faire → P0.3)

---

### P0.3 - Intégration repository avec face_selector ✅
**Fichiers:**
- `facefusion/repository_helper.py` (helper)
- `facefusion/core.py` (processing)
- `facefusion/uis/components/preview.py` (UI previews)

**Problème:** Face selector n'utilise pas repository même si personne sélectionnée

**Solution implémentée:**
- Créé `get_effective_source_paths()` dans repository_helper
- Intégré dans `core.py` pour process_image et process_temp_frame
- Intégré dans `preview.py` pour previews UI
- Logs de debug pour tracer quel mode est utilisé

**Checklist:**
- [x] Créer fonction `get_effective_source_paths()` avec priorité repository > legacy
- [x] Modifier `core.py::process_image()` pour utiliser helper
- [x] Modifier `core.py::process_temp_frame()` pour utiliser helper
- [x] Modifier `preview.py::render()` pour utiliser helper
- [x] Modifier `preview.py::update()` pour utiliser helper
- [x] Ajouter logs debug pour tracer mode actif
- [ ] Tester: swap avec repository → utilise bonnes faces (besoin app running)
- [ ] Tester: swap sans repository → legacy fonctionne (besoin app running)
- [ ] Tester: performance <100ms par frame (besoin app running)

**Temps estimé:** 1h30  
**Temps réel:** 30 min (implémentation core)  
**Statut:** ✅ Complété (tests manuels restent à faire)

---

## 🔧 PRIORITÉ 1 - IMPORTANT (Core Features)

### P1.1 - Fonction create_or_update_person() ✅
**Fichier:** `facefusion_repository/manager.py`

**Problème:** Impossible d'ajouter faces à personne existante via UI

**Solution:**
- Créer `create_or_update_person(name, paths, ...)`
- Détecte si personne existe → appelle `add_faces_to_person()`
- Sinon → appelle `create_person()`

**Checklist:**
- [x] Créer fonction `create_or_update_person()`
- [x] Implémenter logique conditionnelle
- [x] Modifier UI `repository.py::add_person()` pour utiliser nouvelle fonction
- [ ] Tester: ajout à personne existante → merge (besoin de lancer l'app)
- [ ] Tester: nouveau nom → création (besoin de lancer l'app)

**Temps estimé:** 45 min  
**Temps réel:** 15 min  
**Statut:** ✅ Complété (tests manuels à faire)

---

### P1.2 - Fonctions de suppression (person et face) ⏳
**Fichiers:**
- `facefusion_repository/manager.py` (backend)
- `facefusion/uis/components/repository.py` (UI)

**Problème:** Aucune fonction suppression

**Solution:**
```python
# Backend
def remove_person(person_id: str) -> bool
def remove_face_from_person(person_id: str, face_path: str) -> bool

# UI
Delete button dans person card
Remove button dans face gallery
```

**Checklist:**
- [ ] `remove_person()` existe déjà → vérifier fonctionne
- [ ] Créer `remove_face_from_person()`
- [ ] Ajouter bouton "Delete Person" dans UI
- [ ] Ajouter modal confirmation
- [ ] Connecter callbacks
- [ ] Tester: suppression person → fichiers effacés
- [ ] Tester: suppression face → metadata mis à jour

**Temps estimé:** 1h  
**Statut:** ⏳ À faire

---

### P1.3 - Affichage galerie miniatures ⏳
**Fichier:** `facefusion/uis/components/repository.py`

**Problème:** Pas de visualisation des faces

**Solution:**
- Remplacer textbox par Gallery Gradio
- Générer miniatures 200x200px
- Afficher pour personne sélectionnée

**Checklist:**
- [ ] Créer fonction `generate_thumbnail(face_path, size=200)`
- [ ] Remplacer Textbox par gradio.Gallery
- [ ] Charger miniatures lors sélection personne
- [ ] Ajouter overlay avec infos (orientation, quality)
- [ ] Tester: affichage correct
- [ ] Tester: performance avec 20+ faces

**Temps estimé:** 1h30  
**Statut:** ⏳ À faire

---

### P1.4 - Affichage stats personne (face_count, coverage) ⏳
**Fichiers:**
- `facefusion_repository/manager.py`
- `facefusion/uis/components/repository.py`

**Problème:** Stats basiques manquantes

**Solution:**
- Calculer `coverage_stats` lors ajout faces
- Afficher dans person card

**Checklist:**
- [ ] Créer `calculate_coverage_stats(person)` dans manager
- [ ] Appeler lors create/update person
- [ ] Stocker dans person metadata
- [ ] Afficher dans UI: "Coverage: 65%"
- [ ] Ajouter indicateur visuel (◼◼◼◻◻ 60%)
- [ ] Tester: stats correctes

**Temps estimé:** 45 min  
**Statut:** ⏳ À faire

---

## 🎨 PRIORITÉ 2 - UX AVANCÉE (Nice to Have)

### P2.1 - Modal preview avant ajout de faces ⏳
**Fichier:** `facefusion/uis/components/repository.py`

**Problème:** Aucun feedback avant ajout

**Solution:**
- Modal Gradio avec preview images
- Afficher détection face, orientation, quality
- Warnings si overlaps
- Boutons Confirm/Cancel

**Checklist:**
- [ ] Créer fonction `preview_faces_before_add(paths)`
- [ ] Détecter visages dans chaque image
- [ ] Extraire metadata (orientation, quality)
- [ ] Créer modal Gradio
- [ ] Afficher résumé (N added, M skipped, coverage change)
- [ ] Connecter boutons
- [ ] Tester: workflow complet

**Temps estimé:** 2h  
**Statut:** ⏳ À faire

---

### P2.2 - Indicateurs détection/orientation temps réel ⏳
**Fichier:** `facefusion/uis/components/repository.py`

**Problème:** Pas de feedback durant upload

**Solution:**
- Progress bar durant traitement
- Messages par image (✓ Face detected, ✗ No face, ⚠️ Overlap)

**Checklist:**
- [ ] Ajouter gradio.Progress
- [ ] Yield messages durant processing
- [ ] Afficher dans status textbox
- [ ] Tester: messages clairs et utiles

**Temps estimé:** 1h  
**Statut:** ⏳ À faire

---

### P2.3 - Message warning si pas de visage détecté ⏳
**Fichier:** `facefusion_repository/manager.py`

**Solution:**
- Logger.warn() si aucun visage
- Retourner liste skipped_files avec raisons
- Afficher dans UI

**Checklist:**
- [ ] Modifier `create_or_update_person()` pour tracker skips
- [ ] Retourner `{'added': [...], 'skipped': [...]}`
- [ ] Afficher dans UI status
- [ ] Tester: upload image sans visage → warning clair

**Temps estimé:** 30 min  
**Statut:** ⏳ À faire

---

### P2.4 - Affichage overlay metadata sur miniatures ⏳
**Fichier:** `facefusion/uis/components/repository.py`

**Solution:**
- Annotation sur miniatures gallery
- Info: pitch/yaw/roll, quality score

**Checklist:**
- [ ] Générer miniatures avec annotations
- [ ] Utiliser PIL.ImageDraw pour overlay
- [ ] Tester: lisible et utile

**Temps estimé:** 1h  
**Statut:** ⏳ À faire

---

## 🚀 PRIORITÉ 3 - FUTUR (Advanced Features)

### P3.1 - Système test faces pour preview swap ⏳
**Fichiers:**
- `facefusion_repository/test_faces.py` (existe)
- `facefusion/uis/components/repository.py` (intégration)

**Solution:**
- Utiliser `get_test_faces()` existant
- Générer preview swap sur test images
- Afficher comparaison avant/après

**Checklist:**
- [ ] Créer modal "Preview Swap"
- [ ] Charger test faces
- [ ] Appeler processor pour générer swap
- [ ] Afficher galerie comparaison
- [ ] Tester: preview réaliste

**Temps estimé:** 2h  
**Statut:** ⏳ À faire (P3 - optionnel)

---

### P3.2 - Visualisation 3D coverage map ⏳
**Fichiers:**
- Nouveau: `facefusion_repository/coverage_viz.py`
- UI: `facefusion/uis/components/repository.py`

**Solution:**
- Générer plot 3D sphérique avec plotly
- Marquer zones couvertes/manquantes
- Suggestions angles à capturer

**Checklist:**
- [ ] Créer `generate_coverage_plot(person)`
- [ ] Utiliser plotly pour 3D sphere
- [ ] Colorier zones (vert/orange/rouge)
- [ ] Ajouter bouton "View 3D Map" dans UI
- [ ] Tester: visualisation claire

**Temps estimé:** 3h  
**Statut:** ⏳ À faire (P3 - optionnel)

---

## 🧪 TESTS & QUALITÉ

### T1 - Tests unitaires nouveaux comportements ⏳
**Fichiers:** `tests/test_repository_*.py`

**Checklist:**
- [ ] Test unicité noms
- [ ] Test create_or_update_person()
- [ ] Test variables state séparées
- [ ] Test face_selector avec repository
- [ ] Test suppression person/face
- [ ] Test coverage stats calculation
- [ ] Test preview modal
- [ ] Tous tests passent

**Temps estimé:** 2h  
**Statut:** ⏳ À faire

---

### T2 - Tests d'intégration UI ⏳
**Checklist:**
- [ ] Workflow complet: create → add faces → select → swap
- [ ] Switch repository ↔ upload direct
- [ ] Performance: repository 50 persons, 200 faces
- [ ] Memory leak check

**Temps estimé:** 1h  
**Statut:** ⏳ À faire

---

### T3 - Tests de régression ⏳
**Checklist:**
- [ ] CLI commands repository préservés
- [ ] Upload direct (legacy) fonctionne
- [ ] API Python backward compatible
- [ ] Migration v1→v2 automatique

**Temps estimé:** 1h  
**Statut:** ⏳ À faire

---

## 📝 DOCUMENTATION

### D1 - Mise à jour copilot-instructions.md ⏳
**Checklist:**
- [ ] Documenter nouvelles variables state
- [ ] Expliquer modes repository vs upload
- [ ] Ajouter exemples create_or_update_person()
- [ ] Ajouter exemples face_selector intégration

**Temps estimé:** 30 min  
**Statut:** ⏳ À faire

---

### D2 - Mise à jour REPOSITORY.md user doc ⏳
**Checklist:**
- [ ] Screenshots nouvelle UI
- [ ] Workflow utilisateur complet
- [ ] Troubleshooting commun

**Temps estimé:** 45 min  
**Statut:** ⏳ À faire

---

### D3 - Migration guide v1→v2 ⏳
**Checklist:**
- [ ] Expliquer changements breaking
- [ ] Script migration automatique
- [ ] FAQ migration

**Temps estimé:** 30 min  
**Statut:** ⏳ À faire

---

## 📦 DÉPLOIEMENT

### DEP1 - Vérification finale ⏳
**Checklist:**
- [ ] Tous tests passent
- [ ] Pas de warnings linter
- [ ] Performance acceptable
- [ ] Documentation à jour

**Temps estimé:** 30 min  
**Statut:** ⏳ À faire

---

## 🎯 STRATÉGIE D'EXÉCUTION

### Ordre recommandé:
1. **P0.1** → Unicité noms (bloquant fondamental)
2. **P0.2** → State variables (bloquant architecture)
3. **P0.3** → Face selector integration (bloquant fonctionnel)
4. **P1.1** → create_or_update (feature core)
5. **P1.2** → Suppressions (feature core)
6. **P1.3** → Galerie UI (UX important)
7. **P1.4** → Stats coverage (UX important)
8. **T1** → Tests unitaires (validation P0+P1)
9. **P2.1-2.4** → UX avancée (si temps)
10. **T2, T3** → Tests intégration/régression
11. **D1, D2, D3** → Documentation
12. **P3.1, P3.2** → Features avancées (optionnel)
13. **DEP1** → Vérification finale

### Estimation totale:
- **P0 (Bloquants):** ~3h
- **P1 (Important):** ~4h
- **P2 (UX):** ~5h (optionnel)
- **P3 (Futur):** ~5h (optionnel)
- **Tests:** ~4h
- **Docs:** ~2h
- **Total minimum (P0+P1+Tests+Docs):** ~13h
- **Total complet (tout):** ~23h

---

## 📌 NOTES DE PROGRESSION

### Session 2025-10-31 - Partie 1
- ✅ Analysé tous les problèmes
- ✅ Créé REPOSITORY_SPECIFICATIONS.md
- ✅ Créé ce fichier TODO
- ✅ P0.1 Complété: Unicité noms avec normalized_name
- ✅ P1.1 Complété: create_or_update_person()
- ✅ P0.2 Complété: Séparation state variables
- ✅ P0.3 Complété: Intégration repository dans core processing

**✅ TOUS LES BLOQUANTS P0 SONT RÉSOLUS !**

**Fichiers modifiés:**
- `facefusion_repository/types.py` → Ajout normalized_name dans PersonEntry
- `facefusion_repository/manager.py` → _normalize_name(), get_person_by_normalized_name(), create_or_update_person()
- `facefusion/types.py` → Ajout 4 nouvelles clés state pour repository
- `facefusion/repository_helper.py` → NOUVEAU - get_effective_source_paths() et helpers
- `facefusion/core.py` → Intégration get_effective_source_paths() dans processing
- `facefusion/uis/components/repository.py` → Utilise create_or_update_person(), state variables séparées
- `facefusion/uis/components/preview.py` → Intégration get_effective_source_paths() dans previews

### Prochaine session
- [ ] Tests manuels complets (P0.1, P0.2, P0.3)
  - Tester unicité noms
  - Tester ajout faces à personne existante
  - Tester swap avec repository vs direct upload
  - Vérifier performance
- [ ] P1.2: Fonctions suppression (person + face)
- [ ] P1.3: Galerie miniatures
- [ ] P1.4: Stats coverage

---

## 🆘 BLOCAGES & RISQUES

**Aucun blocage identifié pour l'instant.**

**Risques potentiels:**
- Performance avec gros repositories (>100 persons)
  → Mitigation: Lazy loading, pagination
- Breaking changes pour utilisateurs existants
  → Mitigation: Migration automatique v1→v2
- Complexité UI (trop de features)
  → Mitigation: Design progressif, accordéons

---

**Dernière mise à jour:** 2025-10-31 (session initiale)  
**Prochain checkpoint:** Après P0+P1 complétés

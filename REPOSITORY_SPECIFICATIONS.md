# Face Repository System - Specifications Document

**Version:** 2.0  
**Date:** 31 octobre 2025  
**Objectif:** Spécifier le comportement complet du système de repository de visages pour garantir la cohérence des PR futures

---

## 1. VUE D'ENSEMBLE DU SYSTÈME

Le système de repository de visages permet de gérer une bibliothèque de personnes avec leurs photos de visage pour faciliter les opérations de face swap sans avoir à recharger les images sources à chaque fois.

### 1.1 Composants Principaux
- **Storage Layer** (`facefusion_repository/storage.py`) : Persistance JSON + fichiers
- **Manager Layer** (`facefusion_repository/manager.py`) : Logique métier
- **UI Component** (`facefusion/uis/components/repository.py`) : Interface Gradio
- **Selector** (`facefusion_repository/selector.py`) : Sélection intelligente de visages
- **Quality Assessor** : Évaluation qualité multi-critères
- **Orientation System** : Extraction et matching 3D (pitch, yaw, roll)
- **Zone Manager** : Gestion zones de couverture 3D

---

## 2. PROBLÈMES IDENTIFIÉS (État Actuel)

### 2.A. Gestion des Noms de Personnes

#### Symptôme A1: Impossible d'ajouter des images à une personne existante
**Problème:** `create_person()` crée toujours une nouvelle entrée, pas de `add_faces_to_person()` dans l'UI

**Comportement actuel:**
```python
# UI appelle toujours create_person()
person = manager.create_person(person_name, file_paths)
```

**Comportement attendu:**
- Vérifier si la personne existe déjà
- Si oui → `add_faces_to_person(person_id, new_faces)`
- Si non → `create_person(name, faces)`

#### Symptôme A2: Création de doublons de noms
**Problème:** Aucune vérification d'unicité des noms dans `create_person()`

**Comportement actuel:**
- Même nom peut être créé plusieurs fois avec des person_id différents
- `get_person_by_name()` retourne la première occurrence trouvée (arbitraire)

**Comportement attendu:**
- Noms uniques obligatoires (case-insensitive)
- Erreur explicite si tentative de duplication
- OU merge automatique si même nom

#### Symptôme A3: Aucune visualisation des visages dans une personne
**Problème:** UI affiche seulement `display_name (N faces)` sans preview

**Comportement actuel:**
```
• Marie (5 faces)
• Jean (3 faces)
```

**Comportement attendu:**
- Galerie de miniatures cliquables
- Affichage orientation/qualité par visage
- Indicateur de couverture 3D globale

### 2.B. Gestion des Images

#### Symptôme B1: Pas d'informations sur détection/orientation
**Problème:** Aucun feedback visuel durant l'ajout

**Comportement attendu:**
- Indicateur de détection de visage (✓/✗)
- Affichage orientation extraite (pitch/yaw/roll)
- Score qualité en temps réel
- Warning si pas de visage détecté
- Warning si orientation overlap avec existant

#### Symptôme B2: Pas de confirmation avant ajout
**Problème:** Ajout immédiat sans preview

**Comportement attendu:**
- Modal de confirmation avec :
  - Miniatures des visages détectés
  - Métriques qualité
  - Orientations 3D
  - Conflits potentiels (overlaps)
  - Boutons "Confirmer" / "Annuler"

#### Symptôme B3: Impossible de supprimer nom ou photo
**Problème:** Aucune fonction de suppression dans l'UI

**Fonctions manquantes UI:**
- Bouton "Delete Person" dans sélecteur
- Bouton "Remove Face" dans galerie
- Confirmation avant suppression
- Nettoyage fichiers + JSON

### 2.C. Système de Preview 3D

#### Symptôme C1: Pas de prévisualisation 3D du swap
**Problème:** Système preview existe (`facefusion_repository/preview/`) mais pas intégré à l'UI

**Comportement attendu:**
- Modal "Preview Swap" lors de l'ajout
- Modèle 3D de buste tournant (ou vidéo test multi-angles)
- Application swap en temps réel sur différentes orientations
- Identification visuelle des zones de couverture manquantes

#### Symptôme C2: Limites de couverture invisibles
**Problème:** Zone manager calculé mais pas visualisé

**Comportement attendu:**
- Diagramme 3D sphérique montrant :
  - Zones couvertes (vert)
  - Zones manquantes (rouge)
  - Zones partielles (orange)
- Suggestions d'angles manquants à capturer

### 2.D. Conflit Repository vs Source Upload

#### Symptôme D1: Import source bloqué après création de repository
**Problème:** Conflit entre `source_paths` du repository et du file upload

**Comportement actuel:**
```python
# repository.py ligne 152
state_manager.set_item('source_paths', person['face_paths'])

# source.py ligne 57
state_manager.set_item('source_paths', file_names)
```
→ Les deux composants modifient la même state variable

**Comportement attendu:**
- Variables state distinctes :
  - `repository_source_paths` : Visages depuis repository
  - `upload_source_paths` : Upload direct (legacy)
- Priorité repository si personne sélectionnée
- Sinon fallback sur upload direct
- Clear du mode opposé lors du switch

#### Symptôme D2: Impossible de swapper avec nom sélectionné
**Problème:** Sélection repository ne déclenche pas le processing

**Analyse racine:**
1. `update_selected_person()` met à jour `source_paths`
2. Mais composants processors ne réagissent pas au changement
3. Face selector ne cherche pas dans repository

**Comportement attendu:**
- `face_selector.py` intégré avec `RepositorySelector`
- Détection automatique si `repository_person` est set
- Sélection intelligente basée sur orientation target
- Mode "repository" vs "direct upload" explicite

---

## 3. SPÉCIFICATIONS FONCTIONNELLES COMPLÈTES

### 3.1 Création de Personne

```python
def create_or_update_person(
    display_name: str,
    face_paths: List[str],
    quality_threshold: float = 0.7,
    orientation_tolerance: float = 15.0,
    confirm_callback: Optional[Callable] = None
) -> PersonEntry:
    """
    Crée ou met à jour une personne dans le repository.
    
    Comportement:
    1. Normaliser nom (strip, case-insensitive comparison)
    2. Vérifier si personne existe (by normalized name)
    3. Si existe → add_faces_to_person()
    4. Si nouveau → create_person()
    5. Pour chaque image:
       a. Détecter visage (skip si aucun)
       b. Extraire orientation 3D
       c. Calculer métriques qualité
       d. Vérifier overlap orientation
       e. Filtrer si quality < threshold
    6. Appeler confirm_callback avec résumé
    7. Sur confirmation → sauvegarder
    
    Retour:
    - PersonEntry avec face_metadata complet
    - Logs détaillés des faces skipped/added
    """
```

### 3.2 Visualisation Repository

**Interface UI Complète:**

```
┌─────────────────────────────────────────────────┐
│ 📁 Face Repository                              │
├─────────────────────────────────────────────────┤
│                                                  │
│ ➕ Add Person                                   │
│   Name: [______________] [Check Availability]   │
│   Files: [Browse...] (multiple)                 │
│   [Preview & Add]                               │
│                                                  │
├─────────────────────────────────────────────────┤
│ 👤 Persons in Repository (3)                    │
│                                                  │
│ ┌─ Marie (5 faces) ───────────────────┐         │
│ │ [🖼️][🖼️][🖼️][🖼️][🖼️]              │         │
│ │ Coverage: 75% [View 3D Map]          │         │
│ │ [Select] [Add Faces] [Delete]        │         │
│ └──────────────────────────────────────┘         │
│                                                  │
│ ┌─ Jean (3 faces) ─────────────────────┐         │
│ │ [🖼️][🖼️][🖼️]                        │         │
│ │ Coverage: 45% ⚠️ Limited angles      │         │
│ │ [Select] [Add Faces] [Delete]        │         │
│ └──────────────────────────────────────┘         │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 3.3 Preview Modal (Ajout de Visages)

```
┌───────────────────────────────────────────────────┐
│ 🔍 Preview Before Adding - Marie                  │
├───────────────────────────────────────────────────┤
│                                                    │
│ Detected Faces (3/5 images):                      │
│                                                    │
│ ┌─ face1.jpg ────────────────────────┐            │
│ │ [🖼️ Thumbnail]                     │            │
│ │ ✅ Face detected                   │            │
│ │ 📐 Orientation: pitch=5° yaw=-10°  │            │
│ │ ⭐ Quality: 0.85/1.0                │            │
│ │ ✅ New angle (unique)               │            │
│ └────────────────────────────────────┘            │
│                                                    │
│ ┌─ face2.jpg ────────────────────────┐            │
│ │ [🖼️ Thumbnail]                     │            │
│ │ ✅ Face detected                   │            │
│ │ 📐 Orientation: pitch=3° yaw=-8°   │            │
│ │ ⭐ Quality: 0.72/1.0                │            │
│ │ ⚠️  Overlap with existing face #2   │            │
│ │    (existing quality: 0.65)         │            │
│ │ → Will replace (better quality)     │            │
│ └────────────────────────────────────┘            │
│                                                    │
│ ┌─ face3.jpg ────────────────────────┐            │
│ │ [🖼️ Thumbnail]                     │            │
│ │ ❌ No face detected - will skip    │            │
│ └────────────────────────────────────┘            │
│                                                    │
│ Summary:                                           │
│ • 2 faces will be added/replaced                  │
│ • 1 image skipped (no face)                       │
│ • Coverage improvement: 65% → 82%                 │
│                                                    │
│ [View 3D Coverage Map] [Cancel] [Confirm]         │
└───────────────────────────────────────────────────┘
```

### 3.4 Couverture 3D Visualization

```
┌─────────────────────────────────────────────────┐
│ 🌐 3D Orientation Coverage - Marie              │
├─────────────────────────────────────────────────┤
│                                                  │
│         [Sphère 3D Interactive]                 │
│              / | \                              │
│             /  |  \                             │
│            ●───●───●  ← Pitch                   │
│           /    |    \                           │
│          ●     ●     ●                          │
│           \    |    /                           │
│            \   |   /                            │
│             \  |  /                             │
│              \ | /                              │
│                ●                                │
│            ↑       ↑                            │
│          Yaw     Roll                           │
│                                                  │
│ Legend:                                          │
│ 🟢 Covered (5° tolerance)                       │
│ 🟡 Partial (10° tolerance)                      │
│ 🔴 Missing                                       │
│                                                  │
│ Suggestions to improve coverage:                │
│ • Add face with yaw=+30° (right profile)       │
│ • Add face with pitch=-15° (looking down)      │
│                                                  │
│ [Close] [Export Report]                         │
└─────────────────────────────────────────────────┘
```

### 3.5 Swap Preview avec Test Faces

```
┌─────────────────────────────────────────────────┐
│ 🎭 Swap Preview - Testing Marie                │
├─────────────────────────────────────────────────┤
│                                                  │
│ Test Face: [Rotating 3D Bust Model]            │
│            OR [Multi-angle video]               │
│                                                  │
│ Current angle: Yaw=+15°, Pitch=-5°             │
│                                                  │
│ ┌─────────────┬─────────────┐                  │
│ │  Original   │  With Marie  │                  │
│ │  [🖼️]       │  [🖼️]       │                  │
│ └─────────────┴─────────────┘                  │
│                                                  │
│ Quality at this angle: 🟢 Excellent             │
│ Source face used: face2.jpg (closest match)    │
│                                                  │
│ Controls:                                        │
│ Rotation: [◀️] [▶️]  Pitch: [🔼] [🔽]          │
│                                                  │
│ [Play Auto-Rotate] [Export Frames] [Close]     │
└─────────────────────────────────────────────────┘
```

### 3.6 Gestion de State (Résolution Conflit)

```python
# État pour le repository
STATE_KEYS = {
    'repository_mode': bool,           # True si repository actif
    'repository_person_id': str,       # ID personne sélectionnée
    'repository_person_name': str,     # Nom personne
    'repository_source_faces': List[str],  # Chemins faces repository
    
    # État pour upload direct (legacy, fallback)
    'direct_upload_mode': bool,        # True si upload direct
    'source_paths': List[str],         # Upload direct (legacy)
}

# Règles de priorité
def get_effective_source_faces() -> List[str]:
    """
    Retourne les faces sources effectives selon priorité:
    1. Repository si repository_mode=True et person sélectionnée
    2. Sinon fallback sur source_paths (upload direct)
    """
    if state_manager.get_item('repository_mode'):
        repo_faces = state_manager.get_item('repository_source_faces')
        if repo_faces:
            return repo_faces
    
    # Fallback legacy
    return state_manager.get_item('source_paths') or []
```

### 3.7 Intégration avec Face Selector

```python
# Dans face_selector.py ou nouveau module
def select_source_faces(target_frame: VisionFrame) -> List[Face]:
    """
    Sélectionne faces sources intelligemment.
    
    Logique:
    1. Vérifier mode repository vs direct
    2. Si repository:
       a. Extraire orientation du target_frame
       b. Utiliser RepositorySelector.get_best_face_by_orientation()
       c. Fallback sur best-quality si pas de metadata
    3. Si direct upload:
       a. Utiliser logique existante
    
    Retour: Liste de Face objects prêts pour processing
    """
```

---

## 4. ARCHITECTURE DE DONNÉES

### 4.1 Structure PersonEntry (Complète)

```typescript
interface PersonEntry {
  person_id: string;              // UUID unique
  display_name: string;           // Nom affiché (unique, case-insensitive)
  normalized_name: string;        // Pour recherche (lowercase, stripped)
  face_paths: string[];           // Chemins absolus vers images
  face_count: number;             // Nombre de visages
  created_at: string;             // ISO timestamp
  updated_at: string;             // ISO timestamp
  metadata: {
    description?: string;
    tags?: string[];
  };
  face_metadata: {
    [face_path: string]: {
      pose: {
        pitch: number;            // -90 à +90
        yaw: number;              // -180 à +180
        roll: number;             // -180 à +180
      };
      quality: {
        sharpness: number;        // 0.0 à 1.0
        brightness: number;
        contrast: number;
        resolution: number;
        overall: number;          // Weighted average
      };
      zone: CoverageZone;         // Calculé depuis pose
      added_at: string;           // ISO timestamp
      file_size: number;          // Bytes
      dimensions: [number, number]; // [width, height]
    };
  };
  coverage_stats: {
    total_zones: number;
    covered_zones: number;
    coverage_percentage: number;
    missing_angles: Array<{pitch: number, yaw: number}>;
  };
}
```

### 4.2 Repository JSON Structure

```json
{
  "version": "2.0.0",
  "created_at": "2025-10-31T10:00:00Z",
  "updated_at": "2025-10-31T15:30:00Z",
  "persons": {
    "uuid-1234": {
      "person_id": "uuid-1234",
      "display_name": "Marie",
      "normalized_name": "marie",
      "face_paths": [...],
      "face_metadata": {...},
      "coverage_stats": {...}
    }
  },
  "settings": {
    "default_quality_threshold": 0.7,
    "default_orientation_tolerance": 15.0,
    "auto_replace_lower_quality": true
  }
}
```

---

## 5. FLUX DE TRAVAIL UTILISATEUR

### 5.1 Scénario: Ajouter une Première Personne

```
1. Utilisateur clique "Add Person"
2. Entre nom "Marie"
3. Sélectionne 5 images
4. Clique "Preview & Add"
5. Système:
   - Détecte visages (4/5 réussis)
   - Extrait orientations
   - Calcule qualités
   - Affiche modal preview
6. Utilisateur voit:
   - 4 faces OK avec métriques
   - 1 image sans visage (skip)
   - Couverture 3D: 55%
7. Utilisateur clique "Confirm"
8. Système sauvegarde
9. UI refresh → Marie apparaît dans liste
```

### 5.2 Scénario: Ajouter des Visages à Personne Existante

```
1. Utilisateur entre nom "Marie" (existe déjà)
2. Sélectionne 3 nouvelles images
3. Clique "Preview & Add"
4. Système détecte que "Marie" existe
5. Modal preview montre:
   - 2 nouveaux angles uniques → seront ajoutés
   - 1 overlap avec existant:
     * Existant: quality=0.65
     * Nouveau: quality=0.82
     * → Remplacera (meilleure qualité)
6. Affiche "Coverage: 55% → 78%"
7. Sur confirmation → met à jour personne
```

### 5.3 Scénario: Utiliser Repository pour Swap

```
1. Utilisateur sélectionne "Marie" dans dropdown
2. Système:
   - Set repository_mode=True
   - Set repository_person_id=uuid
   - Charge face_paths dans repository_source_faces
3. Upload target video
4. Lance processing
5. Pour chaque frame:
   - Détecte visage target
   - Extrait orientation target
   - Appelle RepositorySelector.get_best_face_by_orientation()
   - Utilise face la plus proche en orientation
6. Résultat: Swap optimal avec transitions fluides
```

### 5.4 Scénario: Fallback Upload Direct (Legacy)

```
1. Utilisateur ne sélectionne AUCUNE personne repository
2. Upload source image via "Source File"
3. Système:
   - Détecte repository_mode=False (ou None)
   - Fallback sur source_paths
   - Utilise logique face_selector classique
4. Processing normal (comportement legacy préservé)
```

---

## 6. CRITÈRES DE VALIDATION

### 6.1 Tests Fonctionnels

- [ ] Création personne avec nom unique
- [ ] Refus doublon de nom (même casse différente)
- [ ] Ajout faces à personne existante
- [ ] Détection et skip images sans visage
- [ ] Calcul et affichage orientations 3D
- [ ] Calcul et affichage scores qualité
- [ ] Détection overlaps orientation
- [ ] Remplacement auto si meilleure qualité
- [ ] Suppression personne + nettoyage fichiers
- [ ] Suppression face individuelle
- [ ] Affichage galerie miniatures
- [ ] Affichage stats couverture 3D
- [ ] Modal preview avant ajout
- [ ] Modal couverture 3D
- [ ] Swap preview avec test faces
- [ ] Sélection repository → processing OK
- [ ] Upload direct fonctionne si pas de repository
- [ ] Pas de conflit entre les deux modes

### 6.2 Tests d'Intégration

- [ ] État synchronisé entre UI components
- [ ] Face selector utilise repository si activé
- [ ] Transitions fluides multi-angles
- [ ] Performance: <100ms pour sélection face
- [ ] Mémoire: Pas de leak avec gros repository
- [ ] Persistance: JSON maintenu cohérent

### 6.3 Tests de Régression

- [ ] Legacy upload direct non cassé
- [ ] CLI repository commands préservés
- [ ] API Python backward compatible
- [ ] Fichiers repository v1.0 migrés auto

---

## 7. MIGRATION v1.0 → v2.0

### 7.1 Détection de Version

```python
def migrate_repository_v1_to_v2(repo_path: str):
    """
    Migre repository v1.0 vers v2.0.
    
    Changements:
    - Ajout normalized_name
    - Recalcul coverage_stats
    - Ajout timestamps si manquants
    - Conversion persons.json → repository.json
    """
```

### 7.2 Backward Compatibility

```python
# Garantir que ancien code continue de fonctionner
manager = RepositoryManager()

# V1 API (préservée)
person = manager.create_person(name, paths)

# V2 API (nouvelle, recommandée)
person = manager.create_or_update_person(
    name, paths, 
    confirm_callback=ui_preview_modal
)
```

---

## 8. DÉPENDANCES & REQUIREMENTS

### 8.1 Bibliothèques Python

```
# requirements.txt additions
Pillow>=10.0.0          # Thumbnails generation
plotly>=5.18.0          # 3D coverage visualization (optionnel)
```

### 8.2 Assets pour Test Faces

```
# À fournir dans .face_repository/test_faces/
- bust_model_3d.obj (optionnel)
- test_video_multiangle.mp4
- test_images/*.jpg (angles variés)
```

---

## 9. DOCUMENTATION POUR PR FUTURES

### 9.1 Checklist PR Repository

Toute PR touchant le repository DOIT:

- [ ] Mettre à jour ce document si comportement changé
- [ ] Ajouter tests pour nouveaux comportements
- [ ] Vérifier backward compatibility
- [ ] Tester migration v1→v2 si structure JSON modifiée
- [ ] Documenter nouvelles variables d'état dans state_manager
- [ ] Vérifier aucun conflit avec modes upload direct/repository
- [ ] Mettre à jour `.github/copilot-instructions.md`

### 9.2 Conventions de Nommage

- `repository_*` : Variables state liées au repository
- `direct_*` ou `upload_*` : Variables upload direct (legacy)
- `*_metadata` : Toujours dictionnaire avec structure définie
- `*_paths` : Toujours liste de strings (chemins absolus)

### 9.3 Logging Standards

```python
# Format logs repository
logger.info(f"[REPO] Creating person '{name}' with {len(paths)} faces")
logger.warn(f"[REPO] Orientation overlap detected: {details}")
logger.error(f"[REPO] Failed to add face: {error}")
```

---

## 10. ROADMAP FUTUR (Hors Scope Actuel)

### Phase 3 (Future)
- Import/export repository (backup)
- Merge/split personnes
- Batch operations
- Repository cloud sync
- Face recognition auto-tagging
- Video source pour auto-extraction multi-angles
- Training custom models depuis repository

---

## RÉSUMÉ EXÉCUTIF

**Problèmes critiques à résoudre:**
1. ✅ Doublon de noms → Unicité forcée
2. ✅ Impossible ajouter faces → create_or_update_person()
3. ✅ Pas de visualisation → Galerie UI
4. ✅ Pas d'info detection → Preview modal
5. ✅ Pas de suppression → Delete functions + UI
6. ✅ Pas de preview 3D → Integration test faces
7. ✅ Conflit repository/upload → Variables state séparées
8. ✅ Impossible swapper → Integration face_selector

**Impact utilisateur:**
- Workflow intuitif et complet
- Feedback visuel permanent
- Pas de surprises (previews systématiques)
- Mode repository et legacy coexistent
- Performance optimisée (sélection intelligente)

**Priorité implémentation:**
1. **P0 (Bloquant):** A2, D1, D2 → Fonctionnement de base
2. **P1 (Important):** A1, B3 → Utilisabilité
3. **P2 (Nice-to-have):** A3, B1, B2 → UX avancée
4. **P3 (Future):** C1, C2 → 3D visualization

---

**Document maintenu par:** AI Coding Agent  
**Dernière révision:** 2025-10-31  
**Prochaine révision:** Après implémentation P0+P1

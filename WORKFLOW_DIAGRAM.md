# Multi-Angle Face Swap Workflow - Visual Guide

## 📊 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREPARATION PHASE                             │
└─────────────────────────────────────────────────────────────────┘

Step 1: COLLECT PHOTOS (Your Person at Different Angles)
═══════════════════════════════════════════════════════════════════
     
     Frontal (0°)        Left Quarter       Right Quarter
         ┌─┐               ┌─┐                 ┌─┐
         │👤│              ◢👤│                 │👤◣
         └─┘               └─┘                 └─┘
      alice_f.jpg       alice_l.jpg         alice_r.jpg
         
     Left Profile       Right Profile
         ┌─┐               ┌─┐
        ◢👤                 👤◣
         └─┘               └─┘
      alice_lp.jpg      alice_rp.jpg

Recommendation: 3-5 angles minimum for good coverage


┌─────────────────────────────────────────────────────────────────┐
│                   CHARACTER CREATION                             │
└─────────────────────────────────────────────────────────────────┘

Step 2: CREATE CHARACTER in GUI
═══════════════════════════════════════════════════════════════════

Open GUI → 👤 Characters Tab → Add Character
    │
    ├─ Name: "Alice"
    ├─ Description: "Main character - multiple angles"
    └─ Click ➕ Add Character
    
Result: char_abc123def456  ← 📋 COPY THIS ID!


┌─────────────────────────────────────────────────────────────────┐
│                     FACE ADDITION                                │
└─────────────────────────────────────────────────────────────────┘

Step 3: ADD FACES TO REPOSITORY
═══════════════════════════════════════════════════════════════════

Go to 📁 Repository Tab → For Each Photo:

┌──────────────────────────────────────────────────────────────┐
│  Upload Image: alice_f.jpg                                   │
│  Name: "Alice - Frontal"                                     │
│  Tags: "frontal"                                             │
│  Character ID: char_abc123def456  ← PASTE THE SAME ID!      │
│  Click ➕ Add Face                                           │
└──────────────────────────────────────────────────────────────┘
         │
         ├─ System Auto-Detects: yaw=2.3°, pitch=1.5°, roll=0.8°
         └─ Saved as: face_001, orientation=0°

Repeat for each angle photo (always use SAME Character ID!)

Result:
┌────────────────────────────────────────────────┐
│ Character: Alice (char_abc123def456)          │
│ ├─ face_001: 0° (Frontal)    quality=0.87     │
│ ├─ face_002: 315° (Left)     quality=0.92     │
│ ├─ face_003: 45° (Right)     quality=0.85     │
│ ├─ face_004: 270° (L Profile) quality=0.88    │
│ └─ face_005: 90° (R Profile) quality=0.84     │
└────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   FACE SWAP EXECUTION                            │
└─────────────────────────────────────────────────────────────────┘

Step 4: PERFORM FACE SWAP
═══════════════════════════════════════════════════════════════════

Go to 🔄 Face Swap Tab:

1. Refresh & Select:
   ┌─────────────────────────────────────────┐
   │ Click: 🔄 Refresh Character List       │
   │ Select: char_abc123def456: Alice        │
   │ Shows: Faces Available: 5               │
   └─────────────────────────────────────────┘

2. Upload Target:
   ┌─────────────────────────────────────────┐
   │ Upload: target_video.mp4                │
   │         (Person moving/turning head)    │
   └─────────────────────────────────────────┘

3. Configure:
   ┌─────────────────────────────────────────┐
   │ Mode: Auto (Best Match per Frame) ✓    │
   │ Output: output/result.mp4 (optional)    │
   └─────────────────────────────────────────┘

4. Execute:
   Click 🎭 Start Face Swap


┌─────────────────────────────────────────────────────────────────┐
│                  AUTOMATIC PROCESSING                            │
└─────────────────────────────────────────────────────────────────┘

WHAT HAPPENS DURING SWAP:
═══════════════════════════════════════════════════════════════════

Frame-by-Frame Analysis:

┌─────────────────────────────────────────────────────────────────┐
│ Frame 1-100: Target Person Frontal (yaw ≈ 0°)                  │
│                                                                  │
│   Target: │👤│  ──→  Match: face_001 (0°)  ──→  Swap!         │
│                       Quality: 0.87                             │
│                       Distance: 2.3° (excellent match)          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Frame 101-200: Target Turns Right (yaw ≈ 40°)                  │
│                                                                  │
│   Target: │👤◣  ──→  Match: face_003 (45°)  ──→  Swap!        │
│                       Quality: 0.85                             │
│                       Distance: 5° (good match)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Frame 201-300: Target Turns Left (yaw ≈ -35°)                  │
│                                                                  │
│   Target: ◢👤│  ──→  Match: face_002 (315°)  ──→  Swap!       │
│                       Quality: 0.92                             │
│                       Distance: 10° (good match)                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Frame 301-400: Target Right Profile (yaw ≈ 85°)                │
│                                                                  │
│   Target: │👤  ──→  Match: face_005 (90°)  ──→  Swap!         │
│                      Quality: 0.84                              │
│                      Distance: 5° (good match)                  │
└─────────────────────────────────────────────────────────────────┘

RESULT: Seamless video with natural-looking swaps at all angles!


┌─────────────────────────────────────────────────────────────────┐
│                      RESULT & DOWNLOAD                           │
└─────────────────────────────────────────────────────────────────┘

Step 5: GET YOUR RESULT
═══════════════════════════════════════════════════════════════════

Progress Window Shows:
┌─────────────────────────────────────────────────┐
│ ✓ Frame 1-100: Using face_001 (0°)            │
│ ✓ Frame 101-200: Using face_003 (45°)         │
│ ✓ Frame 201-300: Using face_002 (315°)        │
│ ✓ Frame 301-400: Using face_005 (90°)         │
│ ✓ Processing complete!                         │
│ ✓ Output saved: output/result.mp4             │
└─────────────────────────────────────────────────┘

Click Download Button to Get Result!
```

---

## 🎯 Key Concepts Explained

### Why Multiple Angles Matter

**Single Face Approach:**
```
Target Video:        Face Used:        Result:
  │👤│ (frontal)  →  │👤│ (frontal)  →  ✓ Natural
  │👤◣ (right)    →  │👤│ (frontal)  →  ✗ Looks flat/wrong
  ◢👤│ (left)     →  │👤│ (frontal)  →  ✗ Looks flat/wrong
```

**Multi-Angle Approach:**
```
Target Video:        Face Used:        Result:
  │👤│ (frontal)  →  │👤│ (frontal)  →  ✓ Natural
  │👤◣ (right)    →  │👤◣ (right)    →  ✓ Natural
  ◢👤│ (left)     →  ◢👤│ (left)     →  ✓ Natural
```

### Automatic Selection Logic

```
For Each Frame:
  1. Detect target face orientation (yaw, pitch, roll)
  2. Compare with all stored faces for character
  3. Calculate angular distance for each:
     distance = |target_yaw - face_yaw| * 1.0 +
                |target_pitch - face_pitch| * 0.5 +
                |target_roll - face_roll| * 0.3
  4. Weight by quality score
  5. Select face with lowest weighted distance
  6. Use that face for swapping this frame
```

### Orientation Angles Reference

```
         0° Frontal
         Looking at camera
              ↑
              │
              │
270° ←───────👤───────→ 90°
Left         │         Right
Profile      │         Profile
              │
              ↓
         180° Back

Common Angles:
  0° = Frontal (straight ahead)
  45° = Right quarter turn
  90° = Right profile
  135° = Right back quarter
  180° = Back of head
  225° = Left back quarter
  270° = Left profile
  315° = Left quarter turn
```

---

## 📋 Quick Reference Checklist

### Before Starting
- [ ] Have 3-5 photos of same person at different angles
- [ ] Photos are high quality (1024x1024+, well-lit, sharp)
- [ ] Repository initialized (`python facefusion_repo_cli.py init`)
- [ ] GUI accessible (`python facefusion.py run --ui-layouts repository`)

### Creating Character Setup
- [ ] Character created in 👤 Characters tab
- [ ] Character ID copied and saved
- [ ] All face photos added in 📁 Repository tab
- [ ] Same Character ID used for ALL faces
- [ ] Faces show different orientations when listed

### Performing Swap
- [ ] Character selected in 🔄 Face Swap tab
- [ ] Character info shows correct face count
- [ ] Target video/image uploaded
- [ ] Mode set to "Auto (Best Match per Frame)"
- [ ] Output path configured (or left empty)

### Verification
- [ ] Character shows multiple faces in details view
- [ ] Statistics tab shows faces at different angles
- [ ] Orientation coverage has multiple angles filled
- [ ] Quality scores acceptable (>0.7 recommended)

---

## 🎨 Orientation Coverage Visualization

### Example Good Coverage

```
Statistics Tab → Orientation Coverage:

  0°:   █████ (5)      ← Frontal faces
 45°:   ███ (3)        ← Right quarter
 90°:   ██ (2)         ← Right profile
135°:   ░ (0)          ← Gap (optional angle)
180°:   ░ (0)          ← Gap (usually not needed)
225°:   ░ (0)          ← Gap (optional angle)
270°:   ██ (2)         ← Left profile
315°:   ███ (3)        ← Left quarter

Coverage: Good! Has frontal + quarters + profiles
```

### Example Poor Coverage

```
  0°:   █████ (5)      ← All faces frontal
 45°:   ░ (0)          ← Missing!
 90°:   ░ (0)          ← Missing!
135°:   ░ (0)
180°:   ░ (0)
225°:   ░ (0)
270°:   ░ (0)          ← Missing!
315°:   ░ (0)          ← Missing!

Coverage: Poor - only frontal faces
Action: Add more angles for better results
```

---

## 💡 Pro Tips Diagram

### Optimal Photo Setup

```
Camera Position:

     [Camera]
        │
        │ 2-3 meters
        ↓
   
Lighting:          Subject:         Background:
   ☀️ ☀️              👤              Plain wall
  (Soft/Even)    (Neutral exp)     (No distraction)

Subject Positioning for Each Angle:

Frontal (0°):           Quarter (±45°):        Profile (±90°):
   [Camera]               [Camera]               [Camera]
      ↓                      ↙                      ←
    👤                    👤                      👤
 Look here!          Turn head              Turn fully
                      halfway
```

---

**Workflow Diagram Version**: 2.0.0  
**Last Updated**: December 10, 2025  
**Purpose**: Visual guide for multi-angle face swap feature

For detailed text instructions, see:
- **MULTI_ANGLE_FACE_SWAP_GUIDE.md** - Complete tutorial
- **GUI_QUICK_REFERENCE.md** - Quick 5-minute guide

# GUI Quick Reference - Multi-Angle Face Swap

## 🎯 Quick Start (5 Minutes)

### Step 1: Create Character (30 seconds)
1. Open **👤 Characters** tab
2. Enter name: "Alice"
3. Click **➕ Add Character**
4. **Copy the character ID** shown (e.g., `char_abc123`)

### Step 2: Add Face Angles (2 minutes)
1. Open **📁 Repository** tab
2. For each photo (frontal, left, right):
   - Upload image
   - Enter name (e.g., "Alice Frontal")
   - Paste character ID in "Character ID" field
   - Click **➕ Add Face**
3. System auto-detects orientation - no manual input needed!

### Step 3: Perform Swap (2 minutes)
1. Open **🔄 Face Swap** tab
2. Click **🔄 Refresh Character List**
3. Select your character from dropdown
4. Upload target video/image
5. Choose "Auto (Best Match per Frame)"
6. Click **🎭 Start Face Swap**

**Done!** System automatically uses best angle for each frame.

---

## 📋 Tab Overview

### 📁 Repository Tab
**Purpose:** Manage individual face images

**Actions:**
- **Add Face:** Upload + optional name, tags, character ID → Add
- **List Faces:** Filter by orientation/character → View all
- **Show Details:** Enter face ID → View full info (orientation, quality, etc.)
- **Remove Face:** Enter face ID → Delete

**Key Fields:**
- `Character ID`: Links face to a character (enables multi-angle)
- `Tags`: Organize faces (e.g., "frontal", "high-quality")
- `Name`: Human-readable label

### 👤 Characters Tab
**Purpose:** Organize faces by person/character

**Actions:**
- **Add Character:** Name + optional description/tags → Create
- **List Characters:** View all with face counts
- **Show Details:** Enter character ID → View associated faces
- **Remove Character:** Enter character ID → Delete (faces remain)

**Important:**
- Character ID is shown after creation - **copy it!**
- One character = one person, multiple faces
- Use for grouping different angles of same person

### 🔄 Face Swap Tab
**Purpose:** Perform face swapping with multi-angle support

**Workflow:**
1. **Refresh** character list
2. **Select** character (your source faces)
3. **Upload** target (video/image to modify)
4. **Choose** mode:
   - Auto (Best Match) - **Recommended** for multi-angle
   - Single Face - Uses one face only
   - All Faces - Experimental multi-angle
5. **Start** swap

**What Happens:**
- System analyzes target face orientation per frame
- Automatically selects best matching face from your character
- Different angles used as target person moves/turns
- Smooth, natural result

### 📊 Statistics Tab
**Purpose:** View repository metrics and coverage

**Information:**
- Total faces in repository
- Average quality score
- Storage size
- Unique characters
- Faces by orientation (0°, 45°, 90°, etc.)
- Orientation coverage visualization

**Use For:**
- Checking if you have good angle coverage
- Finding gaps in orientation angles
- Verifying quality of faces

---

## 🎨 Multi-Angle Face Swap Explained

### Why Multiple Angles?

**Single Face (Traditional):**
```
Target turns left → Frontal face used → ❌ Looks unnatural
Target turns right → Frontal face used → ❌ Looks unnatural
Target frontal → Frontal face used → ✅ Looks good
```

**Multiple Angles (This System):**
```
Target turns left → Left face used → ✅ Looks natural
Target turns right → Right face used → ✅ Looks natural
Target frontal → Frontal face used → ✅ Looks natural
```

### Required Angles (Minimum)

| Priority | Angle | When Used | Example Yaw |
|----------|-------|-----------|-------------|
| ⭐⭐⭐ **Must Have** | Frontal | Person looking forward | 0° ±15° |
| ⭐⭐ **Should Have** | Left Quarter | Person turned left | -30° to -60° |
| ⭐⭐ **Should Have** | Right Quarter | Person turned right | +30° to +60° |
| ⭐ **Nice to Have** | Left Profile | Complete left side | -75° to -105° |
| ⭐ **Nice to Have** | Right Profile | Complete right side | +75° to +105° |

### How Auto-Selection Works

1. **Per Frame:** System analyzes each video frame
2. **Orientation:** Detects target face angle (yaw, pitch, roll)
3. **Matching:** Compares with your stored faces
4. **Selection:** Picks closest angle + highest quality
5. **Swap:** Uses selected face for that frame
6. **Result:** Natural appearance throughout video

---

## 💡 Pro Tips

### Getting Best Results

1. **Photo Quality:**
   - ✅ High resolution (1024x1024+)
   - ✅ Well-lit, no shadows
   - ✅ Sharp focus
   - ✅ Neutral expression
   - ❌ Avoid: blurry, dark, extreme expressions

2. **Angle Coverage:**
   - **Minimum:** 3 angles (frontal, left, right quarter)
   - **Good:** 5 angles (add left/right profiles)
   - **Excellent:** 7+ angles (full coverage)

3. **Consistency:**
   - Same lighting across all photos
   - Same expression (neutral/slight smile)
   - Same time/location if possible
   - Similar distance from camera

4. **Organization:**
   - Use descriptive names: "Alice - Frontal"
   - Add helpful tags: "frontal", "high-quality"
   - One character per person
   - Group all angles under same character ID

### Common Mistakes to Avoid

❌ **Don't:** Add all faces without character ID
✅ **Do:** Always specify character ID when adding faces

❌ **Don't:** Use different character IDs for same person
✅ **Do:** Use same character ID for all angles of one person

❌ **Don't:** Mix photos from different sessions
✅ **Do:** Use photos with consistent lighting/conditions

❌ **Don't:** Use only one angle
✅ **Do:** Add multiple angles for better results

---

## 🔧 Troubleshooting Quick Fixes

### "No characters in dropdown"
→ Click **🔄 Refresh Character List** button

### "Failed to add face"
→ Check image quality (resolution, sharpness, lighting)
→ Try different photo with clearer face

### "Character has 0 faces"
→ Verify you entered Character ID when adding faces
→ Check "Character ID" field in Repository tab
→ Re-add faces with correct ID

### "Orientation seems wrong"
→ Normal! System auto-detects, slight variations expected
→ As long as it's in reasonable range, it works
→ Extreme angles (>75°) rejected automatically

### "Poor swap quality"
→ Add more angle coverage
→ Use higher quality photos
→ Check quality scores in Statistics tab
→ Ensure consistent lighting across angles

---

## 📐 Orientation Guide

### Understanding Angles

```
        0° (Frontal)
           ↑
           |
270° ←---- o ----→ 90°
(Left)     |      (Right)
           |
           ↓
        180° (Back)
```

**Yaw (Horizontal Turn):**
- 0° = Looking at camera
- +45° = Turned right
- -45° = Turned left
- ±90° = Complete profile

**Pitch (Vertical Tilt):**
- 0° = Level
- +20° = Looking down
- -20° = Looking up

**Roll (Head Rotation):**
- 0° = Upright
- ±15° = Slight tilt

### Auto-Detection Examples

When you upload photos, system detects:
```
Photo 1: "Frontal" → Detected: yaw=2°, pitch=-1°, roll=0° → Saved as 0°
Photo 2: "Left turn" → Detected: yaw=-42°, pitch=3°, roll=1° → Saved as 315°
Photo 3: "Right turn" → Detected: yaw=38°, pitch=-2°, roll=-1° → Saved as 45°
```

You don't specify angles - system does it automatically!

---

## 🚀 Keyboard Shortcuts

(When applicable in UI)

- `Ctrl+R` or `F5`: Refresh character list
- `Enter`: Submit current form
- `Esc`: Cancel current operation
- `Tab`: Navigate between fields

---

## 📞 Need More Help?

### Detailed Guides
- **MULTI_ANGLE_FACE_SWAP_GUIDE.md** - Complete step-by-step tutorial
- **COMPLETE_GUIDE.md** - Full system documentation
- **DOCKER.md** - Container deployment guide

### Quick Command Reference
```bash
# Initialize
python facefusion_repo_cli.py init

# Add character (CLI)
python facefusion_repo_cli.py character-add --name "Alice"

# Add face (CLI)
python facefusion_repo_cli.py add --source face.jpg --character char_id

# View stats (CLI)
python facefusion_repo_cli.py stats
```

---

**Quick Reference Version**: 2.0.0  
**Last Updated**: December 10, 2025  
**For**: FaceFusion Repository System Multi-Angle Face Swap Feature

🎭 **Happy face swapping!**

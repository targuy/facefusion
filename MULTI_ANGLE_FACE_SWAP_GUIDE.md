# Multi-Angle Face Swap Guide

## Complete Workflow for Using Multiple Face Angles

**Version**: 2.0.0  
**Date**: December 10, 2025  
**Feature**: Multi-angle face swapping with automatic orientation matching

---

## 🎯 Overview

This guide explains how to use the FaceFusion Repository System to perform face swaps using **multiple face angles from one person**. This feature provides more natural and realistic results when the target person moves or turns their head in different directions.

### Why Use Multiple Angles?

**Traditional Approach (Single Face):**
- Uses one frontal face for all swaps
- Looks unnatural when target turns head
- Limited to frontal or near-frontal angles
- Poor results with profile views

**Multi-Angle Approach (This System):**
- Stores multiple angles of the same person
- Automatically selects best-matching face per frame
- Natural results at all head orientations
- Handles frontal, profile, and everything in between

---

## 📋 Prerequisites

Before starting, ensure you have:

1. ✅ FaceFusion Repository System installed
2. ✅ Multiple photos of the person you want to swap (different angles)
3. ✅ Target video or image where you want to swap faces
4. ✅ Repository initialized: `python facefusion_repo_cli.py init`

### Recommended Face Angles to Collect

For best coverage, collect photos at these orientations:

| Angle | Description | Yaw Range | Essential? |
|-------|-------------|-----------|------------|
| **0° (Frontal)** | Looking straight at camera | -15° to +15° | ✅ Required |
| **45° (Right Quarter)** | Head turned slightly right | +30° to +60° | ✅ Recommended |
| **315° (Left Quarter)** | Head turned slightly left | -30° to -60° | ✅ Recommended |
| **90° (Right Profile)** | Complete right side view | +75° to +105° | ⭐ Optional |
| **270° (Left Profile)** | Complete left side view | -75° to -105° | ⭐ Optional |

💡 **Minimum**: At least 3 angles (frontal + left + right quarter)  
🌟 **Optimal**: 5+ angles covering full range  
🎯 **Professional**: 8+ angles including all standard orientations

---

## 🚀 Complete Workflow

### Method 1: Using the GUI (Recommended for Beginners)

#### Step 1: Create a Character

1. **Open the GUI:**
   ```bash
   python facefusion.py run --ui-layouts repository
   # Access http://localhost:7860
   ```

2. **Go to the "👤 Characters" tab**

3. **Add New Character:**
   - Click "Add Character" section
   - Enter name (e.g., "Alice")
   - Optional: Add description ("Main character - multiple angles")
   - Optional: Add tags (e.g., "protagonist, lead")
   - Click "➕ Add Character"

4. **Note the Character ID:**
   - After creation, you'll see: `char_abc123def456`
   - **Copy this ID** - you'll need it in the next step!

#### Step 2: Add Multiple Face Angles

1. **Go to the "📁 Repository" tab**

2. **Add Frontal Face:**
   - Upload frontal photo (person looking at camera)
   - Name: "Alice - Frontal"
   - Tags: "frontal, 0deg"
   - **Character ID**: `char_abc123def456` (paste the ID from Step 1)
   - Click "➕ Add Face"
   - System automatically detects: `yaw=2.3°, pitch=1.5°, roll=0.8°`

3. **Add Left Quarter Face:**
   - Upload left-turned photo
   - Name: "Alice - Left Quarter"
   - Tags: "left, quarter"
   - **Character ID**: `char_abc123def456` (same ID!)
   - Click "➕ Add Face"
   - System automatically detects: `yaw=-42.1°, pitch=3.2°, roll=-1.1°`

4. **Add Right Quarter Face:**
   - Upload right-turned photo
   - Name: "Alice - Right Quarter"
   - Tags: "right, quarter"
   - **Character ID**: `char_abc123def456` (same ID!)
   - Click "➕ Add Face"
   - System automatically detects: `yaw=38.7°, pitch=-2.1°, roll=0.5°`

5. **Add More Angles (Optional but Recommended):**
   - Repeat for profiles, extreme angles, etc.
   - Always use the **same Character ID**
   - System automatically organizes by orientation

#### Step 3: Verify Your Character

1. **Still in "👤 Characters" tab**

2. **List Characters:**
   - Click "🔍 List Characters"
   - Find your character and note the face count

3. **Show Character Details:**
   - Enter Character ID: `char_abc123def456`
   - Click "👁️ Show Details"
   - Verify all faces are listed with their orientations

**Example Output:**
```
Character Details:
ID: char_abc123def456
Name: Alice
Description: Main character - multiple angles
Faces: 3

Associated Faces:
  • face_20251210_001 (Alice - Frontal): 0°, quality=0.87
    3D: yaw=2.3°, pitch=1.5°, roll=0.8°
  • face_20251210_002 (Alice - Left Quarter): 315°, quality=0.92
    3D: yaw=-42.1°, pitch=3.2°, roll=-1.1°
  • face_20251210_003 (Alice - Right Quarter): 45°, quality=0.85
    3D: yaw=38.7°, pitch=-2.1°, roll=0.5°
```

#### Step 4: Perform Face Swap

1. **Go to the "🔄 Face Swap" tab**

2. **Select Your Character:**
   - Click "🔄 Refresh Character List"
   - Select from dropdown: `char_abc123def456: Alice`
   - Character info displays: "Faces Available: 3"

3. **Upload Target Media:**
   - Click "Target Image or Video"
   - Upload your video (MP4, AVI, MOV) or image (JPG, PNG)

4. **Configure Options:**
   - **Face Selection Mode**: 
     - "Auto (Best Match per Frame)" ← **Recommended**
     - Uses different angles as target person turns
     - "Single Face (Best Overall)" - uses one face throughout
     - "All Faces (Multi-angle)" - experimental mode
   
   - **Output Path**: (optional)
     - Leave empty for auto-generated name
     - Or specify: `output/alice_swap_result.mp4`

5. **Start Swap:**
   - Click "🎭 Start Face Swap"
   - Monitor progress in the progress window
   - Preview shows first frame result
   - Download completed file when ready

#### Step 5: Review Results

1. **Check Progress:**
   - Progress window shows:
     - Which faces are being used
     - Frame-by-frame orientation matching
     - Quality metrics
     - Estimated completion time

2. **Download Result:**
   - Click download button for processed file
   - Or find in specified output path

3. **Review Quality:**
   - Watch the video
   - Check transitions between angles
   - Verify natural appearance at all orientations

---

### Method 2: Using the CLI (For Advanced Users/Automation)

#### Step 1: Create Character

```bash
# Create character
python facefusion_repo_cli.py character-add --name "Alice" --description "Main character"

# Output shows character ID:
# ✓ Character added: char_abc123def456
#   Name: Alice
```

#### Step 2: Add Multiple Face Angles

```bash
# Note: Replace char_abc123def456 with your actual character ID

# Add frontal face
python facefusion_repo_cli.py add \
  --source photos/alice_frontal.jpg \
  --name "Alice - Frontal" \
  --character char_abc123def456

# Add left quarter
python facefusion_repo_cli.py add \
  --source photos/alice_left_quarter.jpg \
  --name "Alice - Left Quarter" \
  --character char_abc123def456

# Add right quarter
python facefusion_repo_cli.py add \
  --source photos/alice_right_quarter.jpg \
  --name "Alice - Right Quarter" \
  --character char_abc123def456

# Add left profile
python facefusion_repo_cli.py add \
  --source photos/alice_left_profile.jpg \
  --name "Alice - Left Profile" \
  --character char_abc123def456

# Add right profile
python facefusion_repo_cli.py add \
  --source photos/alice_right_profile.jpg \
  --name "Alice - Right Profile" \
  --character char_abc123def456
```

#### Step 3: Verify Character

```bash
# List all characters
python facefusion_repo_cli.py character-list

# Show specific character details
python facefusion_repo_cli.py character-show --character-id char_abc123def456

# List faces for this character
python facefusion_repo_cli.py list --character char_abc123def456
```

#### Step 4: Check Orientation Coverage

```bash
# View repository statistics
python facefusion_repo_cli.py stats

# This shows:
# - Total faces
# - Faces by orientation angle
# - Quality metrics
# - Character coverage
```

---

## 🎨 Understanding Automatic Face Selection

### How the System Works

When you perform a face swap with multiple angles:

1. **Frame Analysis:**
   - System processes each frame of target video
   - Detects faces in the frame
   - Calculates orientation (yaw, pitch, roll)

2. **Face Selection:**
   - Compares target face orientation with your stored faces
   - Calculates angular distance for each stored face
   - Weights by quality scores
   - Selects best match

3. **Swap Execution:**
   - Uses the selected face for that frame
   - May use different faces in consecutive frames
   - Ensures smooth transitions

4. **Result:**
   - Natural appearance at all angles
   - Seamless orientation changes
   - Professional-quality output

### Example Scenario

**Your Repository:**
- Face A: 0° (frontal), quality: 0.85
- Face B: 45° (right quarter), quality: 0.90
- Face C: 315° (left quarter), quality: 0.88

**Target Video Frames:**
- Frame 1-100: Person looking forward (0°) → Uses **Face A**
- Frame 101-200: Person turns right (40°) → Uses **Face B**
- Frame 201-250: Person turns back (0°) → Uses **Face A**
- Frame 251-350: Person turns left (-38°) → Uses **Face C**

**Result:** Seamless, natural-looking swap throughout all head movements!

---

## 💡 Best Practices

### Photo Collection Tips

1. **Consistent Conditions:**
   - Same lighting across all angles
   - Same time of day/location if possible
   - Similar expressions (neutral or slight smile)
   - Same distance from camera

2. **Photo Quality:**
   - High resolution (1024x1024 or higher)
   - Well-focused, sharp images
   - Good lighting (no harsh shadows)
   - Clear, unobstructed face view

3. **Angle Coverage:**
   - **Priority 1**: Frontal (0°)
   - **Priority 2**: Left and right quarters (±45°)
   - **Priority 3**: Left and right profiles (±90°)
   - **Priority 4**: Intermediate angles

4. **What to Avoid:**
   - ❌ Extreme expressions (keep neutral)
   - ❌ Accessories that differ between shots
   - ❌ Different hairstyles
   - ❌ Different makeup or glasses
   - ❌ Poor lighting or shadows
   - ❌ Motion blur or low quality

### Organization Tips

1. **Use Descriptive Names:**
   - Good: "Alice - Frontal 0deg"
   - Good: "Bob - Right Profile 90deg"
   - Bad: "IMG_1234"

2. **Add Useful Tags:**
   - Orientation: "frontal", "profile", "quarter"
   - Quality: "high-quality", "studio"
   - Context: "indoor", "outdoor"

3. **One Character Per Person:**
   - Don't mix different people in one character
   - Each person = one unique character
   - Use descriptive character names

---

## 🐛 Troubleshooting

### Problem: Face Not Added

**Error:** "Face quality below threshold"

**Solutions:**
1. Use higher resolution image (min 256x256, recommend 1024x1024+)
2. Improve lighting
3. Use sharper, more focused image
4. Check quality thresholds in configuration

### Problem: Wrong Orientation Detected

**Error:** "Orientation: yaw=85.2° - Expected ~45°"

**Solutions:**
1. System auto-detects orientation - this is normal variation
2. As long as orientation is reasonable, it will work
3. Extreme orientations (>75° yaw) are rejected automatically
4. Try a clearer photo if detection seems very wrong

### Problem: Character Not Showing in Dropdown

**Error:** Dropdown is empty

**Solutions:**
1. Click "🔄 Refresh Character List" button
2. Verify character was created successfully
3. Check character list in "👤 Characters" tab
4. Restart UI if needed

### Problem: No Faces for Character

**Error:** "No faces found for character Alice"

**Solutions:**
1. Verify you used the correct Character ID when adding faces
2. Check "Character ID" field was filled when adding faces
3. List all faces and check their character associations
4. Re-add faces with correct character ID

---

## 📊 Checking Your Setup

### Verify Complete Setup

Use this checklist before performing swap:

```bash
# 1. Check character exists
python facefusion_repo_cli.py character-list
# Should show your character with name

# 2. Check character has faces
python facefusion_repo_cli.py character-show --character-id <YOUR_CHAR_ID>
# Should show multiple associated faces

# 3. Check orientation coverage
python facefusion_repo_cli.py stats
# Should show faces at different angles

# 4. List character's faces
python facefusion_repo_cli.py list --character <YOUR_CHAR_ID>
# Should show all faces with orientations
```

### Optimal Setup Indicators

✅ **Good Setup:**
- 3+ faces per character
- Faces at different angles (0°, 45°, 315°, etc.)
- All faces quality > 0.7
- Clear orientation differences between faces

⚠️ **Needs Improvement:**
- Only 1-2 faces
- All faces at same orientation
- Low quality scores (<0.5)
- Missing key angles (no frontal or no profiles)

---

## 🎯 Advanced Usage

### Multiple Characters in One Video

You can swap multiple people in the same video:

```bash
# Character 1: Alice
python facefusion_repo_cli.py character-add --name "Alice"
# Add Alice's faces with char_alice_id

# Character 2: Bob
python facefusion_repo_cli.py character-add --name "Bob"
# Add Bob's faces with char_bob_id

# Swap both (feature in development)
# Will automatically detect and swap both characters
```

### Batch Processing

Process multiple videos with same character:

```bash
# Setup: One character with multiple angles

# Process video 1
# (Swap using character ID)

# Process video 2
# (Same character ID - reuses faces)

# All use same multi-angle face set
```

### Quality-Based Selection

System automatically considers quality:

- Higher quality faces preferred
- Quality vs orientation trade-off
- Formula: `score = orientation_match_weight * quality_factor`

---

## 📚 Additional Resources

### Related Documentation

- **COMPLETE_GUIDE.md** - Full system documentation
- **DOCKER.md** - Container deployment
- **README_MERGE.md** - Implementation details
- **INTEGRATION_COMPLETE.md** - Technical details

### Example Workflows

See `COMPLETE_GUIDE.md` Section "🎯 Use Cases" for:
- Single Character, Multiple Angles (detailed example)
- Multiple Characters
- Quality-Based Filtering

### Support

- Check troubleshooting section above
- Review logs for error details
- Verify setup using checklist commands

---

## 🎉 Summary

**You've learned:**
1. ✅ Why multiple angles improve face swaps
2. ✅ How to collect and prepare face photos
3. ✅ Complete workflow (GUI and CLI methods)
4. ✅ How automatic face selection works
5. ✅ Best practices and troubleshooting

**Next steps:**
1. Collect 3-5 angle photos of your person
2. Create character and add faces
3. Perform your first multi-angle swap
4. Review results and refine as needed

**Happy face swapping! 🎭**

---

**Version**: 2.0.0  
**Last Updated**: December 10, 2025  
**Status**: Multi-angle face swapping workflow documented and UI ready

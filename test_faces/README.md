# Test Faces for Preview

This directory contains test face images used for generating face swap previews when testing repository faces.

## Usage

Place face images with various orientations in this directory to test face swaps:
- `front_face.jpg` - Frontal face view
- `profile_left.jpg` - Left profile view
- `profile_right.jpg` - Right profile view
- `looking_up.jpg` - Face looking upward
- `looking_down.jpg` - Face looking downward

These test faces will be used to preview how repository faces look when swapped onto different target images.

## How it Works

1. When you click "👁️ Preview Swap" in the Repository UI
2. The system selects the best quality face from your selected person
3. It swaps that face onto one of the test images in this directory
4. The result is displayed in a preview modal

## Recommendations

- Use high-quality, well-lit face images
- Include diverse orientations (front, left, right, up, down)
- Use neutral expressions for consistent previews
- Keep file sizes reasonable (< 5MB per image)
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

## Getting Started

If you don't have test images yet, you can:
1. Use stock photos of faces (ensure you have proper rights)
2. Generate faces using AI tools
3. Use your own photos (be mindful of privacy)

Once you have images, simply drop them into this directory and they'll be automatically detected.

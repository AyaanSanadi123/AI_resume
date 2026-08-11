# Phase 1: Text & Spatial Layout Extraction (`text_extraction.py`)

The extraction module handles raw document intake (PDF and DOCX) while preserving spatial coordinates for multi-column layouts.

## File Validation & Staging
- Validates supported extensions (`.pdf`, `.docx`).
- Secures uploaded files in a temporary environment before processing.

## Multi-Tier PDF Extraction Strategy

### Tier 1: GNN Layouts
- Attempts layout-aware extraction using `pymupdf4llm`.

### Tier 2: Standard Blocks
- Falls back to standard PyMuPDF block extraction if Tier 1 yields no output.

### Tier 3: Smart Tiling OCR
- Automatically triggers PaddleOCR via a lazy-loaded singleton when dealing with scanned or flattened documents.

## Smart Tiling OCR Engine
- Adds a **50px artificial white canvas border** around document images to prevent margin clipping.
- Splits large documents into safe chunks (maximum height of **2200px**) by searching for low-variance uniform gaps.
- Normalizes and translates bounding box coordinates back to the original PDF space.
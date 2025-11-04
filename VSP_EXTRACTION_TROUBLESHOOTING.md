# VSP PDF Extraction Troubleshooting Report

## 🔍 Issue Summary

**Error:** `Permission denied` when attempting to open VSP PDF files for extraction.

**Error Message:**
```
pymupdf.mupdf.FzErrorSystem: code=2: cannot open C:\Users\drlee\AppData\Local\Temp\...pdf: Permission denied
pymupdf.FileDataError: Failed to open file 'C:\Users\drlee\AppData\Local\Temp\...pdf'
```

**Location:** `app/core/extractors/vsp_extractor.py` lines 166, 223, 324

**Affected Function:** `process_vsp_documents()` in `app/core/processor.py`

---

## 🔎 Root Cause Analysis

### The Problem

The recent security update (Phase 2, Step 9) changed temp file handling from `tempfile.mkstemp()` to `tempfile.NamedTemporaryFile(delete=True)`. This introduced a **Windows-specific file locking issue**.

### Why It Happens

1. **File Handle Locking on Windows:**
   - `NamedTemporaryFile(delete=True)` keeps the file handle open while inside the context manager
   - On Windows, when a file is open for writing, it cannot be opened again by another process/reader
   - The file handle remains open until the context manager exits

2. **VSP Extractor Access Pattern:**
   - VSP extractor calls `fitz.open(document_path)` multiple times:
     - Line 166: `_classify_document()` - opens PDF for classification
     - Line 223: `_process_patient_record()` - opens PDF for text extraction
     - Line 324: `_process_lens_enhancement()` - opens PDF for word extraction
   - Each of these calls attempts to open the file while it's still locked by `NamedTemporaryFile`

3. **Why Other Extractors May Work:**
   - Other extractors (EyeMed, Spectera) may not open the PDF file directly
   - They may only use the `document_text` parameter, not `document_path`
   - VSP extractor is unique in requiring direct PDF file access for classification and processing

### Code Flow

```
process_vsp_documents()
  └─> NamedTemporaryFile(delete=True)  # File handle opened here
       ├─> temp_file1.write()           # File locked for writing
       ├─> temp_file1.flush()           # Data written, but handle still open
       ├─> vsp_extractor.extract_from_multiple_files([temp_path1, temp_path2])
       │    └─> _classify_document(temp_path1)  # ❌ FAILS: Permission denied
       │         └─> fitz.open(temp_path1)       # Cannot open: file locked
       └─> Context exits -> file deleted
```

---

## ✅ Fix Options

### Option 1: Close File Handles Before Processing (RECOMMENDED)

**Approach:** Close the temp file handles after writing but before passing paths to the extractor.

**Pros:**
- Maintains automatic cleanup with context manager
- Works on all platforms (Windows, Linux, macOS)
- Minimal code changes
- Preserves security benefits (automatic deletion)

**Cons:**
- Requires careful handle management
- Need to ensure files aren't deleted before extractor finishes

**Implementation:**
```python
# In process_vsp_documents() - app/core/processor.py

with tempfile.NamedTemporaryFile(
    suffix=".pdf",
    prefix=f"{extraction_id}_file1_",
    delete=False  # Change to False
) as temp_file1, tempfile.NamedTemporaryFile(
    suffix=".pdf",
    prefix=f"{extraction_id}_file2_",
    delete=False  # Change to False
) as temp_file2:
    # Write both files to temp locations
    temp_file1.write(file1_content)
    temp_file1.flush()
    temp_path1 = temp_file1.name
    
    temp_file2.write(file2_content)
    temp_file2.flush()
    temp_path2 = temp_file2.name
    
    # Close file handles explicitly to release locks (Windows requirement)
    temp_file1.close()
    temp_file2.close()
    
    try:
        # Now extractor can open the files
        vsp_extractor = VSPExtractor()
        extraction_result = await vsp_extractor.extract_from_multiple_files(
            [temp_path1, temp_path2],
            [file1_name, file2_name]
        )
        # ... rest of processing ...
        
    finally:
        # Manual cleanup since delete=False
        try:
            if os.path.exists(temp_path1):
                os.unlink(temp_path1)
        except OSError:
            pass
        try:
            if os.path.exists(temp_path2):
                os.unlink(temp_path2)
        except OSError:
            pass
```

**Also apply to `process_document()` function** (single file mode).

---

### Option 2: Use TemporaryDirectory + Manual File Creation

**Approach:** Create files in a temporary directory and manually manage them.

**Pros:**
- More explicit control
- Easier to debug
- Files definitely closed before access

**Cons:**
- More code
- Manual cleanup required
- Slightly more complex

**Implementation:**
```python
import tempfile
import shutil

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path1 = os.path.join(temp_dir, f"{extraction_id}_file1.pdf")
    temp_path2 = os.path.join(temp_dir, f"{extraction_id}_file2.pdf")
    
    # Write files (explicitly closed after write)
    with open(temp_path1, 'wb') as f:
        f.write(file1_content)
    with open(temp_path2, 'wb') as f:
        f.write(file2_content)
    
    # Files are now closed, extractor can open them
    vsp_extractor = VSPExtractor()
    extraction_result = await vsp_extractor.extract_from_multiple_files(
        [temp_path1, temp_path2],
        [file1_name, file2_name]
    )
    # ... rest of processing ...
    
# Directory automatically cleaned up on exit
```

---

### Option 3: Write to BytesIO and Pass to Extractor

**Approach:** Modify VSP extractor to accept BytesIO objects instead of file paths.

**Pros:**
- No file system access needed
- No permission issues
- Faster (no disk I/O)

**Cons:**
- Requires changes to VSP extractor
- PyMuPDF fitz.open() may need BytesIO support check
- More invasive change

**Implementation:**
```python
# Would require modifying vsp_extractor.py to accept BytesIO
# fitz.open() may support BytesIO - need to verify
```

**Note:** This option requires checking if PyMuPDF supports BytesIO for `fitz.open()`.

---

## 🎯 Recommended Solution

**Use Option 1** with the following considerations:

1. **Change `delete=True` to `delete=False`** in both:
   - `process_document()` (line 52)
   - `process_vsp_documents()` (lines 166, 170)

2. **Explicitly close file handles** before passing paths to extractor

3. **Add manual cleanup** in finally blocks to ensure files are deleted

4. **Test on Windows** to verify the fix works

---

## 📋 Testing Checklist

After implementing the fix:

- [ ] Test VSP dual-file extraction (file1 + file2)
- [ ] Test VSP single-file extraction (if supported)
- [ ] Verify temp files are cleaned up after processing
- [ ] Verify temp files are cleaned up on exception
- [ ] Test on Windows (primary platform)
- [ ] Test on Linux/macOS (if applicable)
- [ ] Verify no file descriptor leaks
- [ ] Check logs for any permission errors

---

## 🔗 Related Files

- `app/core/processor.py` - Lines 49-134 (process_document), 163-236 (process_vsp_documents)
- `app/core/extractors/vsp_extractor.py` - Lines 166, 223, 324 (fitz.open calls)
- `CODE_QUALITY_ANALYSIS.md` - Phase 2, Step 9 (security update that introduced this)

---

## 📝 Additional Notes

- This issue only manifests on Windows due to stricter file locking
- Linux/macOS may not show this error (but fix still recommended)
- The issue is specific to extractors that open PDF files directly (VSP)
- Other extractors using only text extraction may not be affected

---

**Status:** Ready for implementation
**Priority:** High (blocks VSP extraction functionality)
**Estimated Fix Time:** 30-45 minutes


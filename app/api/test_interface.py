"""
Testing interface for local PDF extraction
"""
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
from datetime import datetime
from pathlib import Path

from app.core.processor import process_document

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/test", response_class=HTMLResponse)
async def test_interface(request: Request):
    """Serve the testing interface"""
    return templates.TemplateResponse("test_interface.html", {"request": request})

@router.post("/test/extract")
async def test_extract(
    file: UploadFile = File(None),
    file1: UploadFile = File(None),
    file2: UploadFile = File(None),
    provider_hint: str = Form(None)
):
    """Extract and save results to test_files/"""
    
    # Determine if this is VSP dual file mode or single file mode
    if provider_hint == "vsp" and file1 and file2:
        # VSP dual file mode
        if not file1.filename.lower().endswith('.pdf') or not file2.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        try:
            # Process both VSP documents
            from app.core.processor import process_vsp_documents
            result = await process_vsp_documents(
                file1_content=await file1.read(),
                file1_name=file1.filename,
                file2_content=await file2.read(),
                file2_name=file2.filename,
                provider_hint=provider_hint
            )
        except ImportError:
            # Fallback to single file processing if multi-file processor doesn't exist
            raise HTTPException(status_code=500, detail="VSP dual file processing not yet implemented")
    
    elif file:
        # Single file mode
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        try:
            # Process the single document
            contents = await file.read()
            result = await process_document(
                file_content=contents,
                filename=file.filename,
                provider_hint=provider_hint
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    
    else:
        raise HTTPException(status_code=400, detail="No files provided for extraction")
    
    try:
        
        # Create test_files directory if it doesn't exist
        test_dir = Path("test_files/results")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine base name based on which files were processed
        if provider_hint == "vsp" and file1 and file2:
            # VSP dual file mode
            base_name1 = Path(file1.filename).stem
            base_name2 = Path(file2.filename).stem
            base_name = f"{base_name1}+{base_name2}"
        else:
            # Single file mode
            base_name = Path(file.filename).stem
            
        result_filename = f"{base_name}_{timestamp}_result.json"
        result_path = test_dir / result_filename
        
        # Save result to file
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": f"Extraction completed successfully!",
            "result_file": str(result_path),
            "provider": result.get("provider"),
            "confidence": result.get("confidence"),
            "processing_time": result.get("processing_time"),
            "data": result.get("data")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import List
from app.models.file import FileMetadata, FileResponse
from app.services.file_service import FileService

router = APIRouter()

@router.post("/files", response_model=FileResponse, status_code=201)
async def upload_file(file: UploadFile = File(...)):
    """Upload de ficheiro"""
    content = await file.read()
    
    metadata = FileService.save_file(
        file_content=content,
        filename=file.filename,
        content_type=file.content_type
    )
    
    return FileResponse(
        message="File uploaded successfully",
        file=metadata
    )

@router.get("/files", response_model=List[FileMetadata])
async def list_files():
    """Listar todos os ficheiros"""
    return FileService.list_files()

@router.get("/files/{file_id}")
async def download_file(file_id: str):
    """Download de ficheiro"""
    content = FileService.get_file(file_id)
    
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return Response(content=content, media_type="application/octet-stream")

@router.put("/files/{file_id}", response_model=FileResponse)
async def update_file(file_id: str, file: UploadFile = File(...)):
    """Atualizar ficheiro existente"""
    content = await file.read()
    
    metadata = FileService.update_file(
        file_id=file_id,
        file_content=content,
        filename=file.filename,
        content_type=file.content_type
    )
    
    if metadata is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        message="File updated successfully",
        file=metadata
    )

@router.delete("/files/{file_id}", response_model=FileResponse)
async def delete_file(file_id: str):
    """Apagar ficheiro"""
    if not FileService.delete_file(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        message="File deleted successfully"
    )
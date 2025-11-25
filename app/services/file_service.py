import os
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.file import FileMetadata
from app.services.metadata_service import MetadataService

STORAGE_PATH = "/mnt/nfs_share"

class FileService:
    
    @staticmethod
    def save_file(file_content: bytes, filename: str, content_type: str) -> FileMetadata:
        """Guarda ficheiro no storage"""
        file_id = str(uuid.uuid4())
        filepath = os.path.join(STORAGE_PATH, file_id)
        
        # Guardar ficheiro
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Criar e guardar metadata
        metadata = FileMetadata(
            id=file_id,
            filename=filename,
            size=len(file_content),
            upload_date=datetime.now(),
            content_type=content_type
        )
        MetadataService.save_metadata(metadata)
        
        return metadata
    
    @staticmethod
    def list_files() -> List[FileMetadata]:
        """Lista todos os ficheiros"""
        return MetadataService.list_metadata()
    
    @staticmethod
    def get_file(file_id: str) -> Optional[bytes]:
        """Obtém conteúdo do ficheiro"""
        filepath = os.path.join(STORAGE_PATH, file_id)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'rb') as f:
            return f.read()
    
    @staticmethod
    def update_file(file_id: str, file_content: bytes, filename: str, content_type: str) -> Optional[FileMetadata]:
        """Atualiza ficheiro existente"""
        filepath = os.path.join(STORAGE_PATH, file_id)
        if not os.path.exists(filepath):
            return None
        
        # Atualizar ficheiro
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Atualizar metadata
        metadata = FileMetadata(
            id=file_id,
            filename=filename,
            size=len(file_content),
            upload_date=datetime.now(),
            content_type=content_type
        )
        MetadataService.save_metadata(metadata)
        
        return metadata
    
    @staticmethod
    def delete_file(file_id: str) -> bool:
        """Apaga ficheiro"""
        filepath = os.path.join(STORAGE_PATH, file_id)
        if not os.path.exists(filepath):
            return False
        
        os.remove(filepath)
        MetadataService.delete_metadata(file_id)
        return True

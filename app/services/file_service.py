import os
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.file import FileMetadata

STORAGE_PATH = "storage"

class FileService:
    
    @staticmethod
    def save_file(file_content: bytes, filename: str, content_type: str) -> FileMetadata:
        """Guarda ficheiro no storage"""
        file_id = str(uuid.uuid4())
        filepath = os.path.join(STORAGE_PATH, file_id)
        
        # Guardar ficheiro
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        # Criar metadata
        metadata = FileMetadata(
            id=file_id,
            filename=filename,
            size=len(file_content),
            upload_date=datetime.now(),
            content_type=content_type
        )
        
        return metadata
    
    @staticmethod
    def list_files() -> List[FileMetadata]:
        """Lista todos os ficheiros"""
        files = []
        for filename in os.listdir(STORAGE_PATH):
            if filename == '.gitkeep':
                continue
            filepath = os.path.join(STORAGE_PATH, filename)
            stat = os.stat(filepath)
            files.append(FileMetadata(
                id=filename,
                filename=filename,
                size=stat.st_size,
                upload_date=datetime.fromtimestamp(stat.st_mtime),
                content_type="application/octet-stream"
            ))
        return files
    
    @staticmethod
    def get_file(file_id: str) -> Optional[bytes]:
        """Obtém conteúdo do ficheiro"""
        filepath = os.path.join(STORAGE_PATH, file_id)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'rb') as f:
            return f.read()
    
    @staticmethod
    def delete_file(file_id: str) -> bool:
        """Apaga ficheiro"""
        filepath = os.path.join(STORAGE_PATH, file_id)
        if not os.path.exists(filepath):
            return False
        
        os.remove(filepath)
        return True

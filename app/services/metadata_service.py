import json
import os
from typing import Dict, Optional
from app.models.file import FileMetadata

METADATA_FILE = "/mnt/nfs-storage/metadata.json"

class MetadataService:
    
    @staticmethod
    def _load() -> Dict[str, dict]:
        """Carrega metadata do ficheiro JSON"""
        if not os.path.exists(METADATA_FILE):
            return {}
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    @staticmethod
    def _save(data: Dict[str, dict]):
        """Guarda metadata no ficheiro JSON"""
        with open(METADATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def save_metadata(metadata: FileMetadata):
        """Adiciona/atualiza metadata de um ficheiro"""
        data = MetadataService._load()
        data[metadata.id] = {
            "id": metadata.id,
            "filename": metadata.filename,
            "size": metadata.size,
            "upload_date": metadata.upload_date.isoformat(),
            "content_type": metadata.content_type
        }
        MetadataService._save(data)
    
    @staticmethod
    def get_metadata(file_id: str) -> Optional[FileMetadata]:
        """Obtém metadata de um ficheiro"""
        data = MetadataService._load()
        if file_id not in data:
            return None
        item = data[file_id]
        return FileMetadata(**item)
    
    @staticmethod
    def list_metadata() -> list:
        """Lista metadata de todos os ficheiros"""
        data = MetadataService._load()
        return [FileMetadata(**item) for item in data.values()]
    
    @staticmethod
    def delete_metadata(file_id: str) -> bool:
        """Remove metadata de um ficheiro"""
        data = MetadataService._load()
        if file_id not in data:
            return False
        del data[file_id]
        MetadataService._save(data)
        return True

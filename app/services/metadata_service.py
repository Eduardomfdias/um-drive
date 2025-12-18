import json
import os
import fcntl
from typing import Dict, Optional
from app.models.file import FileMetadata

METADATA_FILE = "/mnt/nfs_share/metadata.json"

class MetadataService:
    
    @staticmethod
    def _load() -> Dict[str, dict]:
        """Carrega metadata do ficheiro JSON com shared lock"""
        if not os.path.exists(METADATA_FILE):
            return {}
        try:
            with open(METADATA_FILE, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading metadata: {e}")
            return {}
    
    @staticmethod
    def _save(data: Dict[str, dict]):
        """Guarda metadata no ficheiro JSON com exclusive lock"""
        try:
            with open(METADATA_FILE, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2, default=str)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (IOError, OSError) as e:
            print(f"Error saving metadata: {e}")
            raise
    
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
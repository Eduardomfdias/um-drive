import pytest
import os
import tempfile
import shutil
from datetime import datetime
from app.services.file_service import FileService
from app.services.metadata_service import MetadataService

@pytest.fixture
def temp_storage():
    """Criar storage temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    original_storage = FileService.STORAGE_PATH if hasattr(FileService, 'STORAGE_PATH') else '/mnt/nfs_share'
    original_metadata = MetadataService.METADATA_FILE if hasattr(MetadataService, 'METADATA_FILE') else '/mnt/nfs_share/metadata.json'
    
    # Override paths
    import app.services.file_service as fs_module
    import app.services.metadata_service as ms_module
    fs_module.STORAGE_PATH = temp_dir
    ms_module.METADATA_FILE = os.path.join(temp_dir, 'metadata.json')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)
    fs_module.STORAGE_PATH = original_storage
    ms_module.METADATA_FILE = original_metadata


class TestFileService:
    
    def test_save_file(self, temp_storage):
        """Testar guardar ficheiro"""
        content = b"test content"
        filename = "test.txt"
        content_type = "text/plain"
        
        metadata = FileService.save_file(content, filename, content_type)
        
        assert metadata.filename == filename
        assert metadata.size == len(content)
        assert metadata.content_type == content_type
        assert os.path.exists(os.path.join(temp_storage, metadata.id))
    
    def test_get_file(self, temp_storage):
        """Testar ler ficheiro"""
        content = b"test content"
        metadata = FileService.save_file(content, "test.txt", "text/plain")
        
        retrieved = FileService.get_file(metadata.id)
        
        assert retrieved == content
    
    def test_get_nonexistent_file(self, temp_storage):
        """Testar ler ficheiro inexistente"""
        result = FileService.get_file("nonexistent-id")
        assert result is None
    
    def test_list_files(self, temp_storage):
        """Testar listar ficheiros"""
        FileService.save_file(b"content1", "file1.txt", "text/plain")
        FileService.save_file(b"content2", "file2.txt", "text/plain")
        
        files = FileService.list_files()
        
        assert len(files) == 2
        assert all(hasattr(f, 'filename') for f in files)
    
    def test_update_file(self, temp_storage):
        """Testar atualizar ficheiro"""
        original = b"original content"
        updated = b"updated content"
        
        metadata = FileService.save_file(original, "test.txt", "text/plain")
        file_id = metadata.id
        
        new_metadata = FileService.update_file(file_id, updated, "test_updated.txt", "text/plain")
        
        assert new_metadata.id == file_id
        assert new_metadata.filename == "test_updated.txt"
        assert new_metadata.size == len(updated)
        assert FileService.get_file(file_id) == updated
    
    def test_update_nonexistent_file(self, temp_storage):
        """Testar atualizar ficheiro inexistente"""
        result = FileService.update_file("nonexistent-id", b"content", "file.txt", "text/plain")
        assert result is None
    
    def test_delete_file(self, temp_storage):
        """Testar eliminar ficheiro"""
        content = b"test content"
        metadata = FileService.save_file(content, "test.txt", "text/plain")
        file_id = metadata.id
        
        success = FileService.delete_file(file_id)
        
        assert success is True
        assert not os.path.exists(os.path.join(temp_storage, file_id))
        assert FileService.get_file(file_id) is None
    
    def test_delete_nonexistent_file(self, temp_storage):
        """Testar eliminar ficheiro inexistente"""
        result = FileService.delete_file("nonexistent-id")
        assert result is False
    
    def test_concurrent_saves(self, temp_storage):
        """Testar múltiplos saves (simular concorrência)"""
        files = []
        for i in range(5):
            metadata = FileService.save_file(f"content{i}".encode(), f"file{i}.txt", "text/plain")
            files.append(metadata)
        
        all_files = FileService.list_files()
        assert len(all_files) == 5
        
        # Verificar todos os ficheiros existem
        for metadata in files:
            assert FileService.get_file(metadata.id) is not None
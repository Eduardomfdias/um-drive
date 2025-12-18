import pytest
from fastapi.testclient import TestClient
from app.main import app
import tempfile
import shutil
import os

client = TestClient(app)

@pytest.fixture
def temp_storage():
    """Setup storage temporário"""
    temp_dir = tempfile.mkdtemp()
    
    import app.services.file_service as fs_module
    import app.services.metadata_service as ms_module
    fs_module.STORAGE_PATH = temp_dir
    ms_module.METADATA_FILE = os.path.join(temp_dir, 'metadata.json')
    
    yield temp_dir
    
    shutil.rmtree(temp_dir)


class TestAPI:
    
    def test_root_endpoint(self):
        """Testar endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_endpoint(self):
        """Testar health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_upload_file(self, temp_storage):
        """Testar upload de ficheiro"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/files", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert "file" in data
        assert data["file"]["filename"] == "test.txt"
        assert "id" in data["file"]
    
    def test_list_files_empty(self, temp_storage):
        """Testar listar ficheiros (vazio)"""
        response = client.get("/api/files")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_files_with_content(self, temp_storage):
        """Testar listar ficheiros (com conteúdo)"""
        # Upload 2 ficheiros
        client.post("/api/files", files={"file": ("file1.txt", b"content1", "text/plain")})
        client.post("/api/files", files={"file": ("file2.txt", b"content2", "text/plain")})
        
        response = client.get("/api/files")
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_download_file(self, temp_storage):
        """Testar download de ficheiro"""
        # Upload
        content = b"test content for download"
        upload_response = client.post("/api/files", files={"file": ("test.txt", content, "text/plain")})
        file_id = upload_response.json()["file"]["id"]
        
        # Download
        download_response = client.get(f"/api/files/{file_id}")
        assert download_response.status_code == 200
        assert download_response.content == content
    
    def test_download_nonexistent_file(self, temp_storage):
        """Testar download de ficheiro inexistente"""
        response = client.get("/api/files/nonexistent-id")
        assert response.status_code == 404
    
    def test_update_file(self, temp_storage):
        """Testar atualizar ficheiro"""
        # Upload original
        upload_response = client.post("/api/files", files={"file": ("original.txt", b"original", "text/plain")})
        file_id = upload_response.json()["file"]["id"]
        
        # Update
        new_content = b"updated content"
        update_response = client.put(f"/api/files/{file_id}", files={"file": ("updated.txt", new_content, "text/plain")})
        
        assert update_response.status_code == 200
        assert update_response.json()["file"]["filename"] == "updated.txt"
        
        # Verificar conteúdo atualizado
        download = client.get(f"/api/files/{file_id}")
        assert download.content == new_content
    
    def test_update_nonexistent_file(self, temp_storage):
        """Testar atualizar ficheiro inexistente"""
        response = client.put("/api/files/nonexistent-id", files={"file": ("test.txt", b"content", "text/plain")})
        assert response.status_code == 404
    
    def test_delete_file(self, temp_storage):
        """Testar eliminar ficheiro"""
        # Upload
        upload_response = client.post("/api/files", files={"file": ("test.txt", b"content", "text/plain")})
        file_id = upload_response.json()["file"]["id"]
        
        # Delete
        delete_response = client.delete(f"/api/files/{file_id}")
        assert delete_response.status_code == 200
        
        # Verificar que já não existe
        get_response = client.get(f"/api/files/{file_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_file(self, temp_storage):
        """Testar eliminar ficheiro inexistente"""
        response = client.delete("/api/files/nonexistent-id")
        assert response.status_code == 404
    
    def test_metrics_endpoint(self):
        """Testar endpoint de métricas Prometheus"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
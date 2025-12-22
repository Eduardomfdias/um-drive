import sqlite3
import os
from typing import Optional
from datetime import datetime
from app.models.file import FileMetadata

DB_PATH = "/mnt/nfs_share/metadata.db"

class MetadataService:
    
    @staticmethod
    def _init_db():
        """Inicializa base de dados SQLite"""
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para concorrência
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                size INTEGER NOT NULL,
                upload_date TEXT NOT NULL,
                content_type TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    @staticmethod
    def _get_connection():
        """Retorna conexão SQLite com timeout para concorrência"""
        if not os.path.exists(DB_PATH):
            MetadataService._init_db()
        return sqlite3.connect(DB_PATH, timeout=30)
    
    @staticmethod
    def save_metadata(metadata: FileMetadata):
        """Adiciona/atualiza metadata de um ficheiro"""
        conn = MetadataService._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO files (id, filename, size, upload_date, content_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metadata.id,
                metadata.filename,
                metadata.size,
                metadata.upload_date.isoformat(),
                metadata.content_type
            ))
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def get_metadata(file_id: str) -> Optional[FileMetadata]:
        """Obtém metadata de um ficheiro"""
        conn = MetadataService._get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, filename, size, upload_date, content_type FROM files WHERE id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return FileMetadata(
                id=row[0],
                filename=row[1],
                size=row[2],
                upload_date=datetime.fromisoformat(row[3]),
                content_type=row[4]
            )
        finally:
            conn.close()
    
    @staticmethod
    def list_metadata() -> list:
        """Lista metadata de todos os ficheiros"""
        conn = MetadataService._get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, filename, size, upload_date, content_type FROM files ORDER BY upload_date DESC"
            )
            rows = cursor.fetchall()
            return [
                FileMetadata(
                    id=row[0],
                    filename=row[1],
                    size=row[2],
                    upload_date=datetime.fromisoformat(row[3]),
                    content_type=row[4]
                )
                for row in rows
            ]
        finally:
            conn.close()
    
    @staticmethod
    def delete_metadata(file_id: str) -> bool:
        """Remove metadata de um ficheiro"""
        conn = MetadataService._get_connection()
        try:
            cursor = conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    @staticmethod
    def _load():
        """Método legacy para compatibilidade com health check"""
        conn = MetadataService._get_connection()
        conn.close()
        return {}
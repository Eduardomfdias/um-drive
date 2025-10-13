from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileMetadata(BaseModel):
    id: str
    filename: str
    size: int
    upload_date: datetime
    content_type: str

class FileResponse(BaseModel):
    message: str
    file: Optional[FileMetadata] = None

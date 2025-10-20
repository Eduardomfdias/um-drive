# UM Drive - File Storage System

Sistema de armazenamento de ficheiros REST API desenvolvido para a UC de Infraestruturas de Tecnologias de Informação.

## Requisitos
- Python 3.12+
- pip

## Instalação
```bash
# Clonar repositório
git clone [url]
cd um-drive

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Executar
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testar

Aceder a: http://localhost:8000/docs

## Estrutura
```
um-drive/
├── app/
│   ├── main.py           # Entry point
│   ├── api/
│   │   └── endpoints.py  # REST endpoints
│   ├── models/
│   │   └── file.py       # Data models
│   └── services/
│       ├── file_service.py      # File operations
│       └── metadata_service.py  # Metadata management
├── storage/              # File storage
├── requirements.txt
└── README.md
```

## Endpoints

- `POST /api/files` - Upload ficheiro
- `GET /api/files` - Listar ficheiros
- `GET /api/files/{id}` - Download ficheiro
- `PUT /api/files/{id}` - Atualizar ficheiro
- `DELETE /api/files/{id}` - Apagar ficheiro
- test
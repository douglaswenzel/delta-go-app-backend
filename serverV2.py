from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from deepface import DeepFace
from scipy.spatial.distance import euclidean
import numpy as np
import cv2
import json
import uvicorn
import sqlalchemy
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Debug de versões
logging.info("Versões instaladas:")
logging.info(f"SQLAlchemy: {sqlalchemy.__version__}")
try:
    import tensorflow as tf
    logging.info(f"TensorFlow: {tf.__version__}")
except Exception as e:
    logging.error(f"Erro ao importar TensorFlow: {str(e)}")

# Constantes
DATABASE_URL = "sqlite:///./access.db"
THRESHOLD = 10  # Define o limite de similaridade facial (ajustável)

# Inicializa FastAPI
app = FastAPI()

# Configuração do banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de dados
class FacialRecord(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, unique=True, index=True)
    name = Column(String)
    embedding = Column(LargeBinary)  # Armazenado como JSON serializado

# Criação das tabelas
Base.metadata.create_all(bind=engine)

# Dependência para sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função utilitária para processar imagem
def preprocess_image(image_data: bytes) -> np.ndarray:
    img_np = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(img_np, cv2.IMREAD_COLOR)

# Endpoint de registro facial
@app.post("/register")
async def register_user(
    name: str = Form(...),
    person_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if db.query(FacialRecord).filter(FacialRecord.person_id == person_id).first():
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")

    img = preprocess_image(await file.read())

    try:
        embedding_data = DeepFace.represent(img, model_name='Facenet')[0]['embedding']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

    embedding_bytes = json.dumps(embedding_data).encode()
    new_user = FacialRecord(name=name, person_id=person_id, embedding=embedding_bytes)

    db.add(new_user)
    db.commit()

    return {"status": "success", "message": f"Usuário {name} cadastrado com sucesso"}

# Endpoint de verificação facial
@app.post("/verify")
async def verify_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    img = preprocess_image(await file.read())

    try:
        target_embedding = DeepFace.represent(img, model_name='Facenet')[0]['embedding']
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao analisar imagem: {str(e)}")

    best_match = None
    best_distance = float("inf")

    for user in db.query(FacialRecord).all():
        stored_embedding = json.loads(user.embedding.decode())
        distance = euclidean(target_embedding, stored_embedding)

        if distance < best_distance:
            best_distance = distance
            best_match = user

    if best_distance < THRESHOLD:
        return {
            "access": True,
            "user": {
                "name": best_match.name,
                "person_id": best_match.person_id
            },
            "distance": best_distance
        }

    return {
        "access": False,
        "reason": "Rosto não reconhecido",
        "distance": best_distance
    }

# Execução local
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

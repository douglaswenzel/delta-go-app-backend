from fastapi import FastAPI, UploadFile, File
from deepface import DeepFace
import cv2
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

# Verifique as versões instaladas
print("Versões instaladas:")
print(f"SQLAlchemy: {sqlalchemy.__version__}")
try:
    import tensorflow as tf

    print(f"TensorFlow: {tf.__version__}")
except Exception as e:
    print(f"Erro TensorFlow: {str(e)}")

app = FastAPI()

# Configuração do banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./access.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FacialRecord(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(String, unique=True)
    name = Column(String)
    embedding = Column(LargeBinary)


Base.metadata.create_all(bind=engine)


@app.post("/verify")
async def verify_face(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    try:
        # Teste básico do DeepFace
        result = DeepFace.analyze(img, actions=['emotion'])
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructura de datos que viene desde el HTML
class UsuarioRegistro(BaseModel):
    nombre: str
    rol: str
    identificacion: str
    lugar_expedicion: str
    estudios: str
    ocupacion: str
    discapacidad: str
    telefono: str
    correo: str

DB_URL = "sqlite:///./comunidad_elite.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

# Base de datos con todas las columnas nuevas
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    rol = Column(String)
    identificacion = Column(String)
    lugar_expedicion = Column(String)
    estudios = Column(String)
    ocupacion = Column(String)
    discapacidad = Column(String)
    telefono = Column(String)
    correo = Column(String)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/", response_class=HTMLResponse)
def leer_raiz():
    ruta_html = os.path.join(os.path.dirname(__file__), "registro.html")
    try:
        with open(ruta_html, "r", encoding="utf-8") as archivo:
            return archivo.read()
    except Exception:
        return "<h2>Error: No encontré el archivo 'registro.html'.</h2>"

@app.post("/registrar")
def registrar_usuario(usuario: UsuarioRegistro):
    db = SessionLocal()
    try:
        nuevo_usuario = Usuario(
            nombre=usuario.nombre,
            rol=usuario.rol,
            identificacion=usuario.identificacion,
            lugar_expedicion=usuario.lugar_expedicion,
            estudios=usuario.estudios,
            ocupacion=usuario.ocupacion,
            discapacidad=usuario.discapacidad,
            telefono=usuario.telefono,
            correo=usuario.correo
        )
        db.add(nuevo_usuario)
        db.commit()
        return {"status": "ok", "mensaje": f"¡{usuario.nombre} registrado con éxito!"}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error: {str(error)}")
    finally:
        db.close()

@app.get("/usuarios")
def obtener_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        lista_usuarios = []
        for u in usuarios:
            lista_usuarios.append({
                "id": u.id,
                "nombre": u.nombre,
                "rol": u.rol,
                "identificacion": u.identificacion,
                "lugar_expedicion": u.lugar_expedicion,
                "estudios": u.estudios,
                "ocupacion": u.ocupacion,
                "discapacidad": u.discapacidad,
                "telefono": u.telefono,
                "correo": u.correo
            })
        return lista_usuarios
    except Exception as error:
        return {"error": str(error)}
    finally:
        db.close()
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, Field, ValidationError
from ollama import chat
import json

def prompt(fallo_texto):
    return f"""Eres un experto en derecho y análisis de documentos judiciales chilenos. Tu tarea es analizar el siguiente fallo judicial y extraer información estructurada en formato JSON.
Debes extraer los siguientes campos:
1. corte: Tribunal o corte que emitió el fallo 
2. sala: Sala específica del tribunal 
3. fecha: Fecha del fallo en formato "dd-mm-yyyy" 
4. rit: Rol Interno del Tribunal 
5. ruc: Rol Único de Causa 
6. ciudad: Ciudad donde se emitió el fallo 
7. tipo_recurso: Tipo de recurso jurídico 
8. decision: Decisión del tribunal 
9. materia: Materia principal del caso 
10. subMateria: Submateria específica 
11. legislacion: Artículos y leyes citadas 
12. parte_recurrente: Parte que presenta el recurso (si se identifica)
13. parte_recurrida: Parte contra la que se presenta el recurso (si se identifica)
14. resumen_documento: Resumen del contenido del fallo (máx. 500 caracteres)
15. ministros: Lista de ministros participantes
16. voto_disidente: true/false si hay voto disidente

Ejemplo de salida esperada:
{{
    "corte": "Corte Suprema",
    "sala": "Cuarta Sala",
    "fecha": "29-08-2018",
    "rit": "O-87-2025",
    "ruc": "24-4-0621675-2",
    "ciudad": "Santiago",
    "tipo_recurso": "Casación en la forma y en el fondo",
    "decision": "Inadmisible",
    "materia": "Civil",
    "subMateria": "Tercería de posesión",
    "legislacion": "Artículos 766, 767, 781 y 782 del Código de Procedimiento Civil",
    "parte_recurrente": "Juan Pérez",
    "parte_recurrida": "Compañía XYZ",
    "resumen_documento": "El tribunal resolvió que...",
    "ministros": ["Ministro A", "Ministro B"],
    "voto_disidente": false
}}

Responde ÚNICAMENTE con el objeto JSON, sin comentarios ni texto adicional.

FALLO:
{fallo_texto}
"""

class FalloInput(BaseModel):
    fallo: str = Field(..., description="Texto completo del fallo judicial a analizar")

class FalloOutput(BaseModel):
    corte: str = Field(..., description="Tribunal o corte que emitió el fallo", example="Corte Suprema")
    sala: int = Field(..., description="Sala específica del tribunal", example="4")
    fecha: str = Field(..., description="Fecha del fallo en formato dd-mm-yyyy", example="29-08-2018")
    rit: str = Field(..., description="Rol Interno del Tribunal, Es el número de causa dentro de un tribunal específico" , example="O-87-2025")
    ruc: str = Field(..., description="Rol Único de Causa, Es un identificador único a nivel nacional para cada caso judicial" , example="24-4-0621675-2")
    ciudad: str = Field(..., description="Ciudad donde se emitió el fallo", example="Santiago")
    tipo_recurso: str = Field(..., description="Tipo de recurso jurídico", example="Casación en la forma y en el fondo, Apelación, Protección, etc")
    decision: str = Field(..., description="Decisión del tribunal", example="Inadmisible, Acoger, Rechazar, etc")
    materia: str = Field(..., description="Materia principal del caso", example="Civil, Penal, Administrativo, etc")
    subMateria: str = Field(..., description="Submateria específica", example="Tercería de posesión, Prescripción extintiva, etc")
    legislacion: str = Field(..., description="Artículos y leyes citadas", example="Artículos 766, 767, 781 y 782 del Código de Procedimiento Civil")
    parte_recurrente: str = Field(..., description="Parte que presenta el recurso (si se identifica)", example="Juan Pérez")
    parte_recurrida: str = Field(..., description="Parte contra la que se presenta el recurso (si se identifica)", example="Compañía XYZ")
    resumen_documento: str = Field(..., description="Resumen del contenido del fallo (máx. 500 caracteres)", example="El tribunal resolvió que...")
    ministros: list[str] = Field(..., description="Lista de ministros participantes", example=["Ministro A", "Ministro B"])
    voto_disidente: bool = Field(..., description="true/false si hay voto disidente", example=False)



app = FastAPI()

@app.post("/process_fallo", response_model=FalloOutput)
def process_fallo(fallo_input: FalloInput) -> FalloOutput:
    print("Received fallo for processing.")
    fallo_str = fallo_input.fallo
    response = chat(
        model="deepseek-r1:7b",
        options={"temperature": 0.1, "num_predict": 1024},
        messages=[
            {"role": "user", "content": prompt(fallo_str)},
        ]
    )
    content = response["message"]["content"]

    try:
        # Parsear a dict desde JSON
        json_response = json.loads(content)

        # Validar y crear objeto Pydantic
        return FalloOutput(**json_response)

    except json.JSONDecodeError:
        # El LLM no devolvió JSON válido
        raise ValueError(f"Respuesta no es JSON válido: {content}")

    except ValidationError as e:
        # El JSON no cumple con el esquema de Fallo
        raise ValueError(f"Error de validación: {e}\nRespuesta: {content}")
    
if __name__ == "__main__":
    uvicorn.run("ollama_app:app")
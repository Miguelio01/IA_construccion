from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="ML Engine API",
    description="Motor de Inferencia y Machine Learning para procesamiento de planos estructurales.",
    version="1.0.0"
)

class HealthResponse(BaseModel):
    status: str
    service: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        return HealthResponse(status="ok", service="ml-engine")
    except Exception as e:
        # Se exige manejo de excepciones siempre
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

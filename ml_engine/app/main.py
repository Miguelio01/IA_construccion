import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
from typing import List

from app.pipeline.ingestion import extract_lines_from_dxf
from app.pipeline.graph_builder import convert_lines_to_graph
from app.models.gnn import StructuralGNN
import torch

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

class PredictionResponse(BaseModel):
    success: bool
    num_nodes: int
    num_edges: int
    prediction_class: int
    message: str

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_structural_details(file: UploadFile = File(...)):
    """
    Recibe un plano CAD (DXF), extrae la topología (GNN), e infiere características estructurales.
    """
    try:
        # Validar tipo de archivo simple
        if not file.filename.endswith('.dxf'):
            raise HTTPException(status_code=400, detail="Solo se soportan archivos DXF en esta versión.")

        # 1. Guardar temporalmente el archivo subido
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # 2. Extraer líneas (Data Pipeline)
            lines = extract_lines_from_dxf(Path(tmp_path))

            # 3. Convertir a Grafo Pytorch Geometric
            graph_data = convert_lines_to_graph(lines)

            if graph_data.num_nodes == 0:
                return PredictionResponse(
                    success=False,
                    num_nodes=0,
                    num_edges=0,
                    prediction_class=-1,
                    message="No se encontró topología válida en el archivo."
                )

            # 4. Inferencia con Modelo GNN (Dummy prediction para el esqueleto)
            model = StructuralGNN(num_node_features=2, hidden_channels=64, num_classes=2)
            model.eval()

            with torch.no_grad():
                out = model(graph_data.x, graph_data.edge_index)
                prediction = out.argmax(dim=-1).item() # Class 0 o 1

            return PredictionResponse(
                success=True,
                num_nodes=graph_data.num_nodes,
                num_edges=graph_data.num_edges,
                prediction_class=prediction,
                message="Inferencia completada exitosamente."
            )

        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        # Obligatorio manejo de excepciones
        raise HTTPException(status_code=500, detail=f"Fallo durante la inferencia ML: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

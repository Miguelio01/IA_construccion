import torch
import torch.nn.functional as F
from app.models.gnn import StructuralGNN
import logging

logger = logging.getLogger(__name__)

def train_gnn_model(data_loader, epochs: int = 10, hidden_channels: int = 64, num_classes: int = 2):
    """
    Entrena el modelo StructuralGNN con los datos proveídos por data_loader.
    """
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model = StructuralGNN(
            num_node_features=2, # X, Y coordinates
            hidden_channels=hidden_channels,
            num_classes=num_classes
        ).to(device)

        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = torch.nn.CrossEntropyLoss()

        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for data in data_loader:
                try:
                    data = data.to(device)
                    optimizer.zero_grad()
                    out = model(data.x, data.edge_index, data.batch)
                    # Asumimos que data.y es la etiqueta verdadera
                    loss = criterion(out, data.y)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item() * data.num_graphs
                except Exception as batch_e:
                    logger.error(f"Error procesando batch en epoch {epoch}: {batch_e}")
                    raise batch_e

            avg_loss = total_loss / len(data_loader.dataset)
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

        logger.info("Entrenamiento finalizado exitosamente.")
        return model

    except Exception as e:
        logger.error(f"Fallo crítico durante el entrenamiento: {e}")
        raise RuntimeError(f"Error en el training loop: {e}")

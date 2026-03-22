import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool

class StructuralGNN(torch.nn.Module):
    def __init__(self, num_node_features: int, hidden_channels: int, num_classes: int):
        super(StructuralGNN, self).__init__()
        # Definimos 3 capas convolucionales de grafos (GCN)
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        # Capa lineal final para la predicción de clase (ej: tipo de viga o refuerzo)
        self.lin = torch.nn.Linear(hidden_channels, num_classes)

    def forward(self, x, edge_index, batch=None):
        try:
            # Si procesamos un solo grafo sin batch
            if batch is None:
                batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

            # 1. Obtención de embeddings de nodo (Feature learning)
            x = self.conv1(x, edge_index)
            x = x.relu()
            x = F.dropout(x, p=0.5, training=self.training)

            x = self.conv2(x, edge_index)
            x = x.relu()
            x = F.dropout(x, p=0.5, training=self.training)

            x = self.conv3(x, edge_index)

            # 2. Pooling global (Grafo -> Embedding de Grafo)
            x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]

            # 3. Predicción
            out = self.lin(x)

            return out
        except Exception as e:
            # Manejo estricto de excepciones
            raise RuntimeError(f"Fallo durante el forward pass de StructuralGNN: {e}")

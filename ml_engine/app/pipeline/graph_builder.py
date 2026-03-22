import networkx as nx
import torch
from torch_geometric.data import Data
from typing import List
from app.models.structural import Line2D
import logging

logger = logging.getLogger(__name__)

def convert_lines_to_graph(lines: List[Line2D]) -> Data:
    """
    Convierte una lista de líneas (topología 2D) a un grafo PyTorch Geometric.
    Cada intersección o extremo (punto 2D) se convierte en un nodo.
    Las líneas que conectan los puntos son las aristas.
    """
    try:
        graph = nx.Graph()
        node_mapping = {}
        node_idx = 0

        edges = []
        node_features = []

        for line in lines:
            # Redondeamos las coordenadas para evitar problemas de precisión flotante en las intersecciones
            start_coord = (round(line.start.x, 3), round(line.start.y, 3))
            end_coord = (round(line.end.x, 3), round(line.end.y, 3))

            # Registrar nodo inicio si no existe
            if start_coord not in node_mapping:
                node_mapping[start_coord] = node_idx
                node_features.append([start_coord[0], start_coord[1]])
                node_idx += 1

            # Registrar nodo fin si no existe
            if end_coord not in node_mapping:
                node_mapping[end_coord] = node_idx
                node_features.append([end_coord[0], end_coord[1]])
                node_idx += 1

            u = node_mapping[start_coord]
            v = node_mapping[end_coord]
            edges.append([u, v])
            edges.append([v, u]) # Grafo no dirigido

        # Si no hay líneas, devolver un grafo vacío
        if not edges:
            return Data(x=torch.empty((0, 2), dtype=torch.float), edge_index=torch.empty((2, 0), dtype=torch.long))

        # Convertir a tensores de PyTorch
        x = torch.tensor(node_features, dtype=torch.float)
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

        data = Data(x=x, edge_index=edge_index)
        logger.info(f"Grafo generado con {data.num_nodes} nodos y {data.num_edges} aristas dirigidas (doble sentido).")
        return data

    except Exception as e:
        logger.error(f"Error al convertir líneas a grafo: {e}")
        raise ValueError(f"Fallo en la generación del grafo topológico: {e}")

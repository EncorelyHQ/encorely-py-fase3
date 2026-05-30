import numpy as np

CERTIFIED_COMPATIBILITY_THRESHOLD = 0.70

class VibeCalculator:
    """
    Calculador de compatibilidad musical basado en Similitud del Coseno.
    
    Patrón Strategy:
    Encapsula el algoritmo de comparación de vectores para que pueda ser
    intercambiado o mejorado sin afectar a los servicios que lo utilizan.
    """

    @staticmethod
    def calculate(vector_a: dict, vector_b: dict) -> float:
        """
        Calcula el score de compatibilidad entre dos vectores (0.0 a 1.0).
        
        Utiliza Similitud del Coseno sobre las 4 dimensiones core:
        Energy, Danceability, Valence y Tempo.
        """
        # Convertir diccionarios a arrays de NumPy
        a = np.array([
            vector_a.get('energy', 0.0),
            vector_a.get('danceability', 0.0),
            vector_a.get('valence', 0.0),
            vector_a.get('tempo', 0.0)
        ])
        
        b = np.array([
            vector_b.get('energy', 0.0),
            vector_b.get('danceability', 0.0),
            vector_b.get('valence', 0.0),
            vector_b.get('tempo', 0.0)
        ])

        # Cálculo de Similitud del Coseno
        # formula: (A . B) / (||A|| * ||B||)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        similarity = dot_product / (norm_a * norm_b)
        
        # Asegurar que el resultado esté en el rango [0, 1]
        return float(np.clip(similarity, 0.0, 1.0))

    @staticmethod
    def is_compatible(score: float) -> bool:
        """
        Determina si un score cumple el umbral mínimo.
        """
        return score >= CERTIFIED_COMPATIBILITY_THRESHOLD

    @staticmethod
    def normalize_vector(vector: dict) -> dict:
        """
        Normaliza un vector para asegurar que todos los valores estén entre 0 y 1.
        (Útil si se reciben datos de APIs externas con diferentes escalas)
        """
        return {
            k: float(np.clip(v, 0.0, 1.0)) 
            for k, v in vector.items() 
            if k in ['energy', 'danceability', 'valence', 'tempo']
        }

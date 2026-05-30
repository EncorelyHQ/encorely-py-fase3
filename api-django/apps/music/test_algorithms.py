"""
Unit tests for the VibeCalculator algorithm.
Tests the mathematical correctness of the Cosine Similarity calculation.
"""
import pytest
import numpy as np
from apps.music.algorithms import VibeCalculator

def test_vibe_calculator_identity():
    """Vectores idénticos deben tener similitud 1.0"""
    vector = {'energy': 0.8, 'danceability': 0.6, 'valence': 0.5, 'tempo': 0.7}
    score = VibeCalculator.calculate(vector, vector)
    assert score == pytest.approx(1.0)

def test_vibe_calculator_orthogonal():
    """Vectores ortogonales (sin solapamiento) deben tener similitud 0.0"""
    v1 = {'energy': 1.0, 'danceability': 0.0, 'valence': 0.0, 'tempo': 0.0}
    v2 = {'energy': 0.0, 'danceability': 1.0, 'valence': 1.0, 'tempo': 1.0}
    score = VibeCalculator.calculate(v1, v2)
    assert score == pytest.approx(0.0)

def test_vibe_calculator_empty():
    """Vectores vacíos o con ceros deben retornar 0.0"""
    v1 = {}
    v2 = {'energy': 0.5}
    score = VibeCalculator.calculate(v1, v2)
    assert score == 0.0

def test_vibe_calculator_compatibility_threshold():
    """Verifica el umbral de compatibilidad del 70%"""
    assert VibeCalculator.is_compatible(0.75) is True
    assert VibeCalculator.is_compatible(0.65) is False

def test_normalize_vector():
    """Verifica que los valores se clipeen correctamente entre 0 y 1"""
    vector = {'energy': 1.5, 'danceability': -0.5, 'valence': 0.8, 'tempo': 0.2}
    normalized = VibeCalculator.normalize_vector(vector)
    assert normalized['energy'] == 1.0
    assert normalized['danceability'] == 0.0
    assert normalized['valence'] == 0.8
    assert normalized['tempo'] == 0.2

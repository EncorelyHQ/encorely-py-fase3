from __future__ import annotations

import pytest

from app.services.vibe_calculator import VibeCalculator, VibeCalculatorError


def test_identical_vectors_score_one():
    assert VibeCalculator.calculate([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_opposite_vectors_score_zero():
    assert VibeCalculator.calculate([1, 0], [-1, 0]) == pytest.approx(0.0)


def test_orthogonal_vectors_score_half():
    assert VibeCalculator.calculate([1, 0], [0, 1]) == pytest.approx(0.5)


def test_score_is_bounded():
    score = VibeCalculator.calculate([0.8, 0.6, 0.7], [0.7, 0.5, 0.6])
    assert 0.0 <= score <= 1.0


@pytest.mark.parametrize(
    "score,expected",
    [(0.7, "COMPATIBLE"), (0.95, "COMPATIBLE"), (0.69, "NOT_COMPATIBLE"), (0.0, "NOT_COMPATIBLE")],
)
def test_classify_threshold(score, expected):
    assert VibeCalculator.classify(score) == expected


def test_classify_custom_threshold():
    assert VibeCalculator.classify(0.5, threshold=0.4) == "COMPATIBLE"


def test_empty_vector_raises():
    with pytest.raises(VibeCalculatorError):
        VibeCalculator.calculate([], [1])


def test_mismatched_dimensions_raises():
    with pytest.raises(VibeCalculatorError):
        VibeCalculator.calculate([1, 2], [1, 2, 3])


def test_zero_norm_raises():
    with pytest.raises(VibeCalculatorError):
        VibeCalculator.calculate([0, 0], [1, 1])

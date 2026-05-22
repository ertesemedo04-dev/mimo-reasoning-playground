"""Tests for MiMo Reasoning Playground."""

import pytest
from mimo_playground.challenges import CHALLENGES, get_challenges, get_categories, get_difficulties
from mimo_playground.client import MiMoClient, ReasoningStep, ReasoningResponse


class TestChallenges:
    """Test challenge data."""

    def test_challenges_exist(self):
        assert len(CHALLENGES) >= 10

    def test_unique_ids(self):
        ids = [c.id for c in CHALLENGES]
        assert len(ids) == len(set(ids))

    def test_all_have_required_fields(self):
        for c in CHALLENGES:
            assert c.id
            assert c.title
            assert c.category
            assert c.difficulty
            assert c.prompt

    def test_get_challenges_by_category(self):
        logic = get_challenges(category="Logic")
        assert len(logic) >= 1
        assert all(c.category == "Logic" for c in logic)

    def test_get_challenges_by_difficulty(self):
        hard = get_challenges(difficulty="hard")
        assert len(hard) >= 1
        assert all(c.difficulty == "hard" for c in hard)

    def test_get_categories(self):
        cats = get_categories()
        assert "Logic" in cats
        assert "Math" in cats
        assert "Code" in cats

    def test_get_difficulties(self):
        diffs = get_difficulties()
        assert "medium" in diffs
        assert "hard" in diffs


class TestClient:
    """Test MiMo client initialization."""

    def test_client_defaults(self):
        client = MiMoClient()
        assert client.model == "xmtp/mimo-v2.5-pro"
        assert client.max_tokens == 8192
        assert client.temperature == 0.7

    def test_client_custom(self):
        client = MiMoClient(
            api_base="https://custom.api/v1",
            api_key="test-key",
            model="custom-model",
            max_tokens=4096,
            temperature=0.3,
        )
        assert client.api_base == "https://custom.api/v1"
        assert client.api_key == "test-key"
        assert client.model == "custom-model"
        assert client.max_tokens == 4096
        assert client.temperature == 0.3

    def test_reasoning_step(self):
        step = ReasoningStep(index=1, content="test reasoning")
        assert step.index == 1
        assert step.content == "test reasoning"
        assert step.timestamp > 0

    def test_reasoning_response(self):
        resp = ReasoningResponse(
            reasoning_steps=[ReasoningStep(index=1, content="step 1")],
            answer="final answer",
            model="test-model",
            tokens_used=100,
            elapsed_ms=500.0,
        )
        assert len(resp.reasoning_steps) == 1
        assert resp.answer == "final answer"
        assert resp.model == "test-model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

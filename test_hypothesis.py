#!/usr/bin/env python3
"""Test hypothesis component directly."""

import asyncio
import json
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from private_gpt.components.hypothesis.hypothesis_component import HypothesisComponent
from private_gpt.components.reflection.reflection_component import ReflectionRecord

def test_hypothesis_generate():
    """Test hypothesis generation."""
    try:
        # Create a mock reflection record
        reflection = ReflectionRecord(
            id="test_reflection",
            timestamp="2024-01-01T00:00:00Z",
            system_prompt="Test system prompt",
            last_user_message="Test user message",
            chat_history=[],
            assistant_response="Test assistant response",
            sources=[],
            confidence=0.3,  # Low confidence to trigger hypothesis
            reasoning="Test reasoning",
            improvement_suggestions=["Test suggestion"],
            why="Test why field"  # Added the missing required field
        )

        print("Testing hypothesis generation...")
        print(f"Reflection confidence: {reflection.confidence}")

        # This will fail because we need the full dependency injection setup
        # But it will help us see what's happening
        print("Reflection record created successfully")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hypothesis_generate()

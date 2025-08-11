#!/usr/bin/env python3
"""Test LLM component directly."""

import asyncio
import json
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.memory.memory_component import MemoryComponent
from private_gpt.di import global_injector

def test_llm():
    """Test LLM component directly."""
    try:
        print("Testing LLM component...")
        
        # Get LLM component
        llm_component = global_injector.get(LLMComponent)
        print(f"LLM component: {llm_component}")
        
        # Test simple chat
        from llama_index.core.llms import ChatMessage, MessageRole
        
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant. Respond with 'Hello World' only."),
            ChatMessage(role=MessageRole.USER, content="Say hello"),
        ]
        
        print("Sending message to LLM...")
        response = llm_component.llm.chat(messages)
        print(f"Response: {response}")
        
        # Test JSON generation
        system = (
            "You are a goal & hypothesis generator. "
            "Produce STRICT JSON with keys:\n"
            "title, rationale, steps, expected_signal, risks, confidence, priority, tags.\n"
            "Be concise, practical, executable locally. No markdown."
        )
        
        payload = {
            "last_user_message": "Test message",
            "assistant_response": "Test response",
            "reflection": None,
            "relevant_memories": [],
        }
        
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system),
            ChatMessage(role=MessageRole.USER, content=json.dumps(payload, ensure_ascii=False)),
        ]
        
        print("Testing JSON generation...")
        response = llm_component.llm.chat(messages)
        print(f"JSON Response: {response}")
        
        # Try to parse the response
        if hasattr(response, 'message') and response.message:
            text = response.message.content
        else:
            text = str(response)
            
        print(f"Response text: {text}")
        
        # Try to extract JSON
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                parsed = json.loads(json_str)
                print(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
        else:
            print("No JSON found in response")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm()

#!/usr/bin/env python3
"""Test chat API and auto-hypothesis generation."""

import requests
import json
import time

def test_chat_and_hypothesis():
    """Test chat API and check for auto-hypothesis generation."""
    base_url = "http://localhost:8000"
    
    # Test 1: Simple chat completion
    print("Testing chat completion...")
    chat_payload = {
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "use_context": False,
        "include_sources": False,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=chat_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat completed successfully!")
            print(f"Response: {result.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ Failed to complete chat: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Wait a bit for reflection and hypothesis generation
    print("\nWaiting for reflection and hypothesis generation...")
    time.sleep(3)
    
    # Test 2: Check if any hypotheses were generated
    print("\nChecking for auto-generated hypotheses...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=10")
        
        if response.status_code == 200:
            hypotheses = response.json()
            auto_hypotheses = [h for h in hypotheses if "auto" in h.get('tags', [])]
            
            print(f"✅ Found {len(hypotheses)} total hypotheses")
            print(f"✅ Found {len(auto_hypotheses)} auto-generated hypotheses")
            
            for i, hyp in enumerate(auto_hypotheses):
                print(f"  Auto {i+1}. {hyp.get('title')} (ID: {hyp.get('id')})")
                print(f"      Tags: {hyp.get('tags')}")
                print(f"      Confidence: {hyp.get('confidence')}")
                print(f"      Reflection confidence: {hyp.get('derived_from', {}).get('reflection_confidence')}")
        else:
            print(f"❌ Failed to list hypotheses: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try a more complex question that might trigger low confidence
    print("\nTesting complex question for low confidence...")
    complex_payload = {
        "messages": [
            {"role": "user", "content": "Explain quantum physics in detail and how it relates to consciousness"}
        ],
        "use_context": False,
        "include_sources": False,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=complex_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Complex chat completed successfully!")
            print(f"Response length: {len(result.get('response', ''))}")
        else:
            print(f"❌ Failed to complete complex chat: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Wait again
    print("\nWaiting for reflection and hypothesis generation...")
    time.sleep(3)
    
    # Check hypotheses again
    print("\nChecking for new auto-generated hypotheses...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=10")
        
        if response.status_code == 200:
            hypotheses = response.json()
            auto_hypotheses = [h for h in hypotheses if "auto" in h.get('tags', [])]
            
            print(f"✅ Total hypotheses: {len(hypotheses)}")
            print(f"✅ Auto-generated hypotheses: {len(auto_hypotheses)}")
            
            for i, hyp in enumerate(auto_hypotheses):
                print(f"  Auto {i+1}. {hyp.get('title')} (ID: {hyp.get('id')})")
                print(f"      Tags: {hyp.get('tags')}")
                print(f"      Confidence: {hyp.get('confidence')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_and_hypothesis()

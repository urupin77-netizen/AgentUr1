#!/usr/bin/env python3
"""Test hypothesis API endpoints."""

import requests
import json

def test_hypothesis_api():
    """Test hypothesis API endpoints."""
    base_url = "http://localhost:8000"
    
    # Test 1: Generate hypothesis
    print("Testing hypothesis generation...")
    payload = {
        "last_user_message": "Test message",
        "assistant_response": "Test response",
        "reflection": None,
        "top_memory_limit": 5,
        "tags": ["test"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/hypothesis/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hypothesis generated successfully!")
            print(f"Title: {result.get('title')}")
            print(f"ID: {result.get('id')}")
            print(f"Tags: {result.get('tags')}")
            
            # Save ID for status update test
            hypothesis_id = result.get('id')
        else:
            print(f"❌ Failed to generate hypothesis: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: List hypotheses
    print("\nTesting hypothesis list...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=5")
        
        if response.status_code == 200:
            hypotheses = response.json()
            print(f"✅ Found {len(hypotheses)} hypotheses")
            for i, hyp in enumerate(hypotheses):
                print(f"  {i+1}. {hyp.get('title')} (ID: {hyp.get('id')}) - Status: {hyp.get('status')}")
        else:
            print(f"❌ Failed to list hypotheses: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Update hypothesis status
    print(f"\nTesting hypothesis status update for ID: {hypothesis_id}")
    try:
        update_payload = {
            "id": hypothesis_id,
            "status": "in_progress"
        }
        
        response = requests.post(
            f"{base_url}/v1/hypothesis/update_status",
            json=update_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status updated successfully!")
            print(f"New status: {result.get('status')}")
        else:
            print(f"❌ Failed to update status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Clear all hypotheses
    print("\nTesting hypothesis clear...")
    try:
        response = requests.post(f"{base_url}/v1/hypothesis/clear")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hypotheses cleared successfully!")
            print(f"Response: {result}")
        else:
            print(f"❌ Failed to clear hypotheses: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Verify list is empty
    print("\nVerifying hypotheses are cleared...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=5")
        
        if response.status_code == 200:
            hypotheses = response.json()
            print(f"✅ List shows {len(hypotheses)} hypotheses (should be 0)")
        else:
            print(f"❌ Failed to list hypotheses: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hypothesis_api()

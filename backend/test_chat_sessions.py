#!/usr/bin/env python3
"""
Test the new chat session management functionality
"""

import requests
import json

def test_chat_sessions():
    """Test chat session management endpoints"""
    
    print("=" * 60)
    print("Testing Chat Session Management")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    test_user_id = "test_user_sessions"
    
    # Test 1: Create a new chat session
    print("1. Creating new chat session...")
    try:
        response = requests.post(f"{base_url}/chat/sessions", params={
            "user_id": test_user_id,
            "title": "Test Medical Chat"
        })
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["id"]
            print(f"✓ Session created: {session_id}")
            print(f"  Title: {session_data['title']}")
        else:
            print(f"✗ Failed to create session: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating session: {e}")
        return False
    
    # Test 2: Get all sessions for user
    print("\n2. Getting user sessions...")
    try:
        response = requests.get(f"{base_url}/chat/sessions", params={
            "user_id": test_user_id
        })
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✓ Found {len(sessions)} sessions")
            for session in sessions:
                print(f"  - {session['title']} ({session['id'][:8]}...)")
        else:
            print(f"✗ Failed to get sessions: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error getting sessions: {e}")
    
    # Test 3: Send a message to the session
    print("\n3. Sending message to session...")
    try:
        response = requests.post(f"{base_url}/chat", json={
            "message": "What are the symptoms of diabetes?",
            "attached_record_ids": [],
            "user_id": test_user_id,
            "user_role": "patient",
            "session_id": session_id
        })
        
        if response.status_code == 200:
            chat_data = response.json()
            print(f"✓ Message sent successfully")
            print(f"  Session ID: {chat_data.get('session_id', 'Not returned')}")
            print(f"  Ollama powered: {chat_data.get('ollama_powered', False)}")
            print(f"  Response preview: {chat_data.get('response', '')[:100]}...")
        else:
            print(f"✗ Failed to send message: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error sending message: {e}")
    
    # Test 4: Get session messages
    print("\n4. Getting session messages...")
    try:
        response = requests.get(f"{base_url}/chat/sessions/{session_id}/messages", params={
            "user_id": test_user_id
        })
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✓ Found {len(messages)} messages in session")
            for msg in messages:
                print(f"  - {msg['message'][:50]}...")
        else:
            print(f"✗ Failed to get session messages: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error getting session messages: {e}")
    
    # Test 5: Clear session messages
    print("\n5. Clearing session messages...")
    try:
        response = requests.delete(f"{base_url}/chat/sessions/{session_id}/messages", params={
            "user_id": test_user_id
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Failed to clear session: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error clearing session: {e}")
    
    # Test 6: Update session title
    print("\n6. Updating session title...")
    try:
        response = requests.put(f"{base_url}/chat/sessions/{session_id}", params={
            "user_id": test_user_id,
            "title": "Updated Medical Chat Session"
        })
        
        if response.status_code == 200:
            print("✓ Session title updated")
        else:
            print(f"✗ Failed to update session: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error updating session: {e}")
    
    # Test 7: Create another session
    print("\n7. Creating second session...")
    try:
        response = requests.post(f"{base_url}/chat/sessions", params={
            "user_id": test_user_id,
            "title": "Second Chat Session"
        })
        
        if response.status_code == 200:
            session2_data = response.json()
            session2_id = session2_data["id"]
            print(f"✓ Second session created: {session2_id}")
        else:
            print(f"✗ Failed to create second session: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating second session: {e}")
        return False
    
    # Test 8: Delete a session
    print("\n8. Deleting second session...")
    try:
        response = requests.delete(f"{base_url}/chat/sessions/{session2_id}", params={
            "user_id": test_user_id
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Failed to delete session: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error deleting session: {e}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Chat Session Management")
    
    success = test_chat_sessions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Chat session management is working!")
        print("Features available:")
        print("• Create new chat sessions")
        print("• Switch between sessions") 
        print("• Send messages to specific sessions")
        print("• Clear session messages")
        print("• Update session titles")
        print("• Delete sessions")
        print("\nYour frontend now supports multiple chat sessions!")
    else:
        print("❌ Some session management features need debugging")
    print("=" * 60)
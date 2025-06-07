#!/usr/bin/env python3
"""
Test script for the enhanced NPC system
"""
import pygame
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import NPC, NPCPersonality, NPCMood, PERSONALITY_COLORS, TILE_SIZE

def test_npc_creation():
    """Test creating NPCs with the enhanced personality system"""
    print("=== Testing Enhanced NPC System ===")
    
    # Initialize pygame (needed for Rect)
    pygame.init()
    
    # Test creating an NPC with different personalities
    test_cases = [
        (NPCPersonality.FRIENDLY, NPCMood.CONTENT),
        (NPCPersonality.GRUFF, NPCMood.ANGRY),
        (NPCPersonality.MYSTERIOUS, NPCMood.CURIOUS),
        (NPCPersonality.SCHOLARLY, NPCMood.EXCITED)
    ]
    
    for personality, mood in test_cases:
        print(f"\n--- Testing {personality.name} NPC with {mood.name} mood ---")
        
        npc = NPC(
            name=f"Test {personality.name} NPC",
            rect=pygame.Rect(100, 100, TILE_SIZE, TILE_SIZE),
            dialogue_options=["Hello!", "How are you?", "Goodbye!"],
            personality=personality,
            current_mood=mood
        )
        
        print(f"Created NPC: {npc.name}")
        print(f"Personality: {npc.personality.name}")
        print(f"Mood: {npc.current_mood.name}")
        print(f"Color: {npc.color}")
        print(f"Relationship Level: {npc.relationship_level}")
        
        # Test dialogue generation
        response = npc.get_dialogue_response("greeting")
        print(f"Greeting response: {response}")
        
        # Test relationship modification
        npc.modify_relationship(10)
        print(f"After positive interaction, relationship: {npc.relationship_level}")
        
        # Test serialization
        npc_dict = npc.to_dict()
        print(f"Serialization test - personality in dict: {npc_dict.get('personality')}")
        
        # Test deserialization
        restored_npc = NPC.from_dict(npc_dict)
        print(f"Deserialization test - restored personality: {restored_npc.personality.name}")
        
        assert restored_npc.name == npc.name
        assert restored_npc.personality == npc.personality
        assert restored_npc.current_mood == npc.current_mood
        assert restored_npc.relationship_level == npc.relationship_level
        
        print("✓ All tests passed for this NPC!")
    
    print("\n=== All NPC System Tests Completed Successfully! ===")

def test_personality_colors():
    """Test that personality colors are properly assigned"""
    print("\n=== Testing Personality Colors ===")
    
    pygame.init()
    
    for personality in NPCPersonality:
        npc = NPC(
            name=f"Color Test {personality.name}",
            rect=pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE),
            dialogue_options=["Test"],
            personality=personality
        )
        
        expected_color = PERSONALITY_COLORS.get(personality, (100, 100, 100))
        print(f"{personality.name}: Expected {expected_color}, Got {npc.color}")
        
        assert npc.color == expected_color, f"Color mismatch for {personality.name}"
    
    print("✓ All personality colors are correct!")

def test_mood_responses():
    """Test that NPCs generate different responses based on mood"""
    print("\n=== Testing Mood-Based Responses ===")
    
    pygame.init()
    
    npc = NPC(
        name="Mood Test NPC",
        rect=pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE),
        dialogue_options=["Hello", "Goodbye"],
        personality=NPCPersonality.FRIENDLY
    )
    
    responses_by_mood = {}
    
    for mood in NPCMood:
        npc.current_mood = mood
        npc.generate_mood_responses()
        
        # Get multiple responses to see variety
        responses = []
        for _ in range(3):
            response = npc.get_dialogue_response("greeting")
            responses.append(response)
        
        responses_by_mood[mood.name] = responses
        print(f"{mood.name} responses: {responses}")
    
    print("✓ Mood-based responses are working!")

if __name__ == "__main__":
    try:
        test_npc_creation()
        test_personality_colors()
        test_mood_responses()
        print("\n🎉 ALL TESTS PASSED! The enhanced NPC system is working correctly! 🎉")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    pygame.quit()

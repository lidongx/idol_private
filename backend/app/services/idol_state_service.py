"""
Idol State Service for managing idol life rhythm
Story 5.1: 偶像状态系统与生活节奏引擎
"""
import json
import random
import os
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.models.idol_state import IdolState
from app.models.idol import Idol


class IdolStateService:
    """
    Service for managing idol states and life rhythm

    This service handles the "living" aspect of idols - their daily schedules,
    mood changes, energy levels, making them feel more real and alive.
    """

    def __init__(self, db: Session):
        self.db = db
        self.schedule_config = self._load_schedule_config()

    def _load_schedule_config(self) -> Dict:
        """
        Load idol daily schedule configuration from JSON file

        Returns:
            Dictionary with schedule configuration
        """
        config_path = os.path.join(
            os.path.dirname(__file__),
            '../config/idol_schedule.json'
        )

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to default config
            return self._get_default_schedule()

    def _get_default_schedule(self) -> Dict:
        """
        Get default schedule configuration (fallback)

        Returns:
            Default schedule dictionary
        """
        return {
            "daily_schedule": {
                "0-7": {"status": "sleeping", "mood": "calm", "energy": 20},
                "7-9": {"status": "waking_up", "mood": "calm", "energy": 60},
                "9-12": {"status": "active", "mood": "happy", "energy": 80},
                "12-14": {"status": "resting", "mood": "calm", "energy": 70},
                "14-18": {"status": "working", "mood": "focused", "energy": 75},
                "18-20": {"status": "active", "mood": "relaxed", "energy": 80},
                "20-22": {"status": "resting", "mood": "calm", "energy": 60},
                "22-24": {"status": "preparing_sleep", "mood": "tired", "energy": 40},
            },
            "mood_transitions": {
                "calm": ["happy", "thoughtful"],
                "happy": ["excited", "calm"],
                "tired": ["calm", "sleepy"]
            }
        }

    def get_state_for_hour(self, hour: int) -> Dict:
        """
        Get recommended state for a specific hour

        Args:
            hour: Hour of day (0-23)

        Returns:
            Dictionary with status, mood, energy, and optional message
        """
        schedule = self.schedule_config.get('daily_schedule', {})

        # Get state for this hour
        hour_key = str(hour)
        if hour_key in schedule:
            state = schedule[hour_key].copy()
            # Pick a random message if available
            if 'messages' in state and state['messages']:
                state['message'] = random.choice(state['messages'])
                del state['messages']
            return state

        # Fallback to default
        return {"status": "active", "mood": "calm", "energy": 70}

    def get_random_mood_transition(self, current_mood: str) -> str:
        """
        Get a random mood transition from current mood

        Args:
            current_mood: Current mood

        Returns:
            New mood (may be same if no transitions defined)
        """
        transitions = self.schedule_config.get('mood_transitions', {})

        if current_mood in transitions:
            possible_moods = transitions[current_mood]
            if possible_moods:
                return random.choice(possible_moods)

        return current_mood

    def get_idol_state(self, idol_id: int) -> Optional[IdolState]:
        """
        Get current state for an idol

        Args:
            idol_id: Idol ID

        Returns:
            IdolState object or None
        """
        return (
            self.db.query(IdolState)
            .filter(IdolState.idol_id == idol_id)
            .first()
        )

    def initialize_idol_state(self, idol_id: int) -> IdolState:
        """
        Initialize state for an idol (create if not exists)

        Args:
            idol_id: Idol ID

        Returns:
            Created or existing IdolState
        """
        # Check if state already exists
        existing_state = self.get_idol_state(idol_id)
        if existing_state:
            return existing_state

        # Get current hour's recommended state
        current_hour = datetime.now().hour
        initial_state = self.get_state_for_hour(current_hour)

        # Create new state
        idol_state = IdolState(
            idol_id=idol_id,
            current_status=initial_state['status'],
            current_mood=initial_state['mood'],
            energy_level=initial_state['energy'],
            status_message=initial_state.get('message')
        )

        self.db.add(idol_state)
        self.db.commit()
        self.db.refresh(idol_state)

        return idol_state

    def update_idol_state(
        self,
        idol_id: int,
        apply_mood_variation: bool = True
    ) -> IdolState:
        """
        Update idol state based on current time

        Args:
            idol_id: Idol ID
            apply_mood_variation: Whether to apply random mood changes (20% chance)

        Returns:
            Updated IdolState
        """
        # Get or create state
        idol_state = self.get_idol_state(idol_id)
        if not idol_state:
            return self.initialize_idol_state(idol_id)

        # Get current hour's recommended state
        current_hour = datetime.now().hour
        recommended_state = self.get_state_for_hour(current_hour)

        # Update status and base energy
        new_status = recommended_state['status']
        new_mood = recommended_state['mood']
        new_energy = recommended_state['energy']

        # Apply random mood variation (20% chance)
        if apply_mood_variation and random.random() < 0.2:
            new_mood = self.get_random_mood_transition(idol_state.current_mood)

        # Apply small random energy variation (±5)
        energy_variation = random.randint(-5, 5)
        new_energy = max(0, min(100, new_energy + energy_variation))

        # Update state
        idol_state.update_state(
            status=new_status,
            mood=new_mood,
            energy=new_energy,
            message=recommended_state.get('message')
        )

        self.db.commit()
        self.db.refresh(idol_state)

        return idol_state

    def update_all_idol_states(self) -> List[IdolState]:
        """
        Update states for all active idols

        This is called by the hourly background task

        Returns:
            List of updated IdolState objects
        """
        # Get all active idols
        active_idols = (
            self.db.query(Idol)
            .filter(Idol.is_active == True)
            .all()
        )

        updated_states = []

        for idol in active_idols:
            try:
                updated_state = self.update_idol_state(idol.id, apply_mood_variation=True)
                updated_states.append(updated_state)
            except Exception as e:
                print(f"Error updating state for idol {idol.id}: {e}")

        return updated_states

    def get_state_display_info(self, idol_id: int) -> Optional[Dict]:
        """
        Get display-friendly state information

        Args:
            idol_id: Idol ID

        Returns:
            Dictionary with formatted state info or None
        """
        idol_state = self.get_idol_state(idol_id)

        if not idol_state:
            return None

        return {
            'status': idol_state.current_status,
            'status_text': idol_state.status_display_name,
            'mood': idol_state.current_mood,
            'mood_text': idol_state.mood_display_name,
            'energy_level': idol_state.energy_level,
            'energy_text': idol_state.energy_display,
            'status_message': idol_state.status_message,
            'is_available': idol_state.is_available,
            'is_sleeping': idol_state.is_sleeping,
            'updated_at': idol_state.updated_at.isoformat() if idol_state.updated_at else None
        }

    def force_update_state(
        self,
        idol_id: int,
        status: str,
        mood: str,
        energy: int,
        message: str = None
    ) -> IdolState:
        """
        Force update idol state to specific values (admin/testing)

        Args:
            idol_id: Idol ID
            status: New status
            mood: New mood
            energy: New energy level
            message: Optional status message

        Returns:
            Updated IdolState
        """
        idol_state = self.get_idol_state(idol_id)
        if not idol_state:
            idol_state = self.initialize_idol_state(idol_id)

        idol_state.update_state(
            status=status,
            mood=mood,
            energy=energy,
            message=message
        )

        self.db.commit()
        self.db.refresh(idol_state)

        return idol_state

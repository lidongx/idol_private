"""
Background task for automatic memory extraction

Runs periodically to extract memories from idle conversations
"""
import asyncio
import threading
from typing import Optional
from datetime import datetime

from app.database import SessionLocal
from app.services.memory_extraction_service import MemoryExtractionService


class MemoryExtractionTask:
    """
    Background task for automatic memory extraction

    Usage:
        task = MemoryExtractionTask(interval_minutes=5)
        task.start()  # Start background thread
        task.stop()   # Stop background thread
    """

    def __init__(self, interval_minutes: int = 5, idle_minutes: int = 5):
        """
        Initialize memory extraction task

        Args:
            interval_minutes: How often to check for idle conversations (default: 5)
            idle_minutes: Minimum idle time before extraction (default: 5)
        """
        self.interval_minutes = interval_minutes
        self.idle_minutes = idle_minutes
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the background task"""
        if self.running:
            print("[MemoryExtractionTask] Already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[MemoryExtractionTask] Started (interval: {self.interval_minutes}min, idle: {self.idle_minutes}min)")

    def stop(self):
        """Stop the background task"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("[MemoryExtractionTask] Stopped")

    def _run_loop(self):
        """Main loop running in background thread"""
        while self.running:
            try:
                # Run extraction
                asyncio.run(self._extract_memories())

            except Exception as e:
                print(f"[MemoryExtractionTask] Error in extraction loop: {e}")

            # Sleep until next run
            for _ in range(self.interval_minutes * 60):
                if not self.running:
                    break
                threading.Event().wait(1)

    async def _extract_memories(self):
        """Extract memories from idle conversations"""
        db = SessionLocal()

        try:
            extraction_service = MemoryExtractionService(db)

            # Get conversations needing extraction
            conversations = extraction_service.get_conversations_needing_extraction(
                idle_minutes=self.idle_minutes
            )

            if not conversations:
                print(f"[MemoryExtractionTask] No idle conversations found")
                return

            print(f"[MemoryExtractionTask] Found {len(conversations)} idle conversations")

            # Extract memories from each conversation
            for conversation in conversations:
                try:
                    print(f"[MemoryExtractionTask] Extracting from conversation {conversation.id}")

                    memories = await extraction_service.extract_memories_from_conversation(
                        conversation_id=conversation.id,
                        message_limit=20,
                    )

                    print(f"[MemoryExtractionTask] Extracted {len(memories)} memories from conversation {conversation.id}")

                except Exception as e:
                    print(f"[MemoryExtractionTask] Failed to extract from conversation {conversation.id}: {e}")
                    continue

        except Exception as e:
            print(f"[MemoryExtractionTask] Task failed: {e}")

        finally:
            db.close()


# Global task instance
_memory_extraction_task: Optional[MemoryExtractionTask] = None


def start_memory_extraction_task(interval_minutes: int = 5, idle_minutes: int = 5):
    """
    Start the global memory extraction task

    Args:
        interval_minutes: Check interval (default: 5)
        idle_minutes: Minimum idle time (default: 5)
    """
    global _memory_extraction_task

    if _memory_extraction_task and _memory_extraction_task.running:
        print("[MemoryExtractionTask] Task already running")
        return

    _memory_extraction_task = MemoryExtractionTask(
        interval_minutes=interval_minutes,
        idle_minutes=idle_minutes,
    )
    _memory_extraction_task.start()


def stop_memory_extraction_task():
    """Stop the global memory extraction task"""
    global _memory_extraction_task

    if _memory_extraction_task:
        _memory_extraction_task.stop()
        _memory_extraction_task = None


def get_memory_extraction_task() -> Optional[MemoryExtractionTask]:
    """Get the global memory extraction task instance"""
    return _memory_extraction_task

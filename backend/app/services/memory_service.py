"""
Memory service for storing and retrieving user memories
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.memory import Memory, MemoryTag
from app.services.chromadb_client import get_user_collection
from app.services.embedding_service import generate_embedding


class MemoryService:
    """
    Service for managing user memories with vector search

    Provides:
    - Store memories in PostgreSQL + ChromaDB
    - Semantic search using vector similarity
    - Memory tagging and categorization
    """

    def __init__(self, db: Session):
        self.db = db

    async def add_memory(
        self,
        user_id: int,
        content: str,
        memory_type: Optional[str] = None,
        importance: str = "medium",
        source_message_id: Optional[int] = None,
    ) -> Memory:
        """
        Add a new memory for a user

        Steps:
        1. Create memory record in PostgreSQL
        2. Generate embedding vector
        3. Store vector in ChromaDB

        Args:
            user_id: User ID
            content: Memory content text
            memory_type: Type of memory (hobby, work, family, feeling, goal, preference, event)
            importance: Importance level (low, medium, high)
            source_message_id: Optional reference to source message

        Returns:
            Created Memory object
        """
        # Validate inputs
        if not content or not content.strip():
            raise ValueError("Memory content cannot be empty")

        if importance not in ["low", "medium", "high"]:
            raise ValueError("Importance must be: low, medium, or high")

        # 1. Create memory in PostgreSQL
        memory = Memory(
            user_id=user_id,
            content=content.strip(),
            memory_type=memory_type,
            importance=importance,
            source_message_id=source_message_id,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        try:
            # 2. Generate embedding
            embedding = await generate_embedding(content)

            # 3. Store in ChromaDB
            collection = get_user_collection(user_id)
            embedding_id = f"mem_{memory.id}"

            collection.add(
                documents=[content],
                embeddings=[embedding],
                ids=[embedding_id],
                metadatas=[{
                    "memory_id": memory.id,
                    "memory_type": memory_type or "general",
                    "importance": importance,
                    "created_at": memory.created_at.isoformat(),
                }]
            )

            # Update memory with embedding_id
            memory.embedding_id = embedding_id
            self.db.commit()
            self.db.refresh(memory)

            print(f"[Memory] Added memory {memory.id} for user {user_id}")

        except Exception as e:
            print(f"[Memory] Failed to add vector to ChromaDB: {e}")
            # Keep memory in PostgreSQL even if vector storage fails
            # Vector can be regenerated later if needed

        return memory

    async def search_memories(
        self,
        user_id: int,
        query: str,
        limit: int = 3,
        memory_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity

        Args:
            user_id: User ID
            query: Search query text
            limit: Maximum number of results (default: 3)
            memory_type: Optional filter by memory type

        Returns:
            List of memory results with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = await generate_embedding(query)

            # Search in ChromaDB
            collection = get_user_collection(user_id)

            # Build where clause for filtering
            where = None
            if memory_type:
                where = {"memory_type": memory_type}

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
            )

            # Parse results
            memories = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    memory_id = results['metadatas'][0][i].get('memory_id')

                    # Fetch full memory from database
                    memory = self.db.query(Memory).filter(
                        Memory.id == memory_id,
                        Memory.user_id == user_id,
                    ).first()

                    if memory:
                        memories.append({
                            "memory": memory,
                            "distance": results['distances'][0][i],
                            "similarity": 1 - results['distances'][0][i],  # Convert distance to similarity
                        })

            return memories

        except Exception as e:
            print(f"[Memory] Search failed: {e}")
            return []

    def get_user_memories(
        self,
        user_id: int,
        memory_type: Optional[str] = None,
        importance: Optional[str] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """
        Get user memories with optional filters

        Args:
            user_id: User ID
            memory_type: Optional filter by type
            importance: Optional filter by importance
            limit: Maximum number of results

        Returns:
            List of Memory objects
        """
        query = self.db.query(Memory).filter(Memory.user_id == user_id)

        if memory_type:
            query = query.filter(Memory.memory_type == memory_type)

        if importance:
            query = query.filter(Memory.importance == importance)

        query = query.order_by(Memory.created_at.desc()).limit(limit)

        return query.all()

    def mark_memory_mentioned(self, memory_id: int) -> bool:
        """
        Update last_mentioned_at timestamp for a memory

        Called when AI mentions this memory in conversation

        Args:
            memory_id: Memory ID

        Returns:
            True if updated successfully
        """
        memory = self.db.query(Memory).filter(Memory.id == memory_id).first()

        if memory:
            memory.mark_mentioned()
            self.db.commit()
            return True

        return False

    def delete_memory(self, user_id: int, memory_id: int) -> bool:
        """
        Delete a memory

        Args:
            user_id: User ID (for authorization)
            memory_id: Memory ID

        Returns:
            True if deleted successfully
        """
        memory = self.db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.user_id == user_id,
        ).first()

        if not memory:
            return False

        # Delete from ChromaDB
        if memory.embedding_id:
            try:
                collection = get_user_collection(user_id)
                collection.delete(ids=[memory.embedding_id])
            except Exception as e:
                print(f"[Memory] Failed to delete from ChromaDB: {e}")

        # Delete from PostgreSQL
        self.db.delete(memory)
        self.db.commit()

        return True

    # ========== Memory Tags ==========

    def set_tag(self, user_id: int, tag_name: str, tag_value: str) -> MemoryTag:
        """
        Set or update a user tag

        Tags are key-value pairs for user attributes
        Examples: name=张三, job=软件工程师, city=北京, birthday=1995-05-20

        Args:
            user_id: User ID
            tag_name: Tag name
            tag_value: Tag value

        Returns:
            MemoryTag object
        """
        # Check if tag exists
        tag = self.db.query(MemoryTag).filter(
            MemoryTag.user_id == user_id,
            MemoryTag.tag_name == tag_name,
        ).first()

        if tag:
            # Update existing tag
            tag.tag_value = tag_value
            tag.updated_at = datetime.utcnow()
        else:
            # Create new tag
            tag = MemoryTag(
                user_id=user_id,
                tag_name=tag_name,
                tag_value=tag_value,
            )
            self.db.add(tag)

        self.db.commit()
        self.db.refresh(tag)

        return tag

    def get_tag(self, user_id: int, tag_name: str) -> Optional[str]:
        """
        Get a user tag value

        Args:
            user_id: User ID
            tag_name: Tag name

        Returns:
            Tag value or None if not found
        """
        tag = self.db.query(MemoryTag).filter(
            MemoryTag.user_id == user_id,
            MemoryTag.tag_name == tag_name,
        ).first()

        return tag.tag_value if tag else None

    def get_all_tags(self, user_id: int) -> Dict[str, str]:
        """
        Get all tags for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary of tag_name -> tag_value
        """
        tags = self.db.query(MemoryTag).filter(
            MemoryTag.user_id == user_id
        ).all()

        return {tag.tag_name: tag.tag_value for tag in tags}

    def delete_tag(self, user_id: int, tag_name: str) -> bool:
        """
        Delete a user tag

        Args:
            user_id: User ID
            tag_name: Tag name

        Returns:
            True if deleted successfully
        """
        tag = self.db.query(MemoryTag).filter(
            MemoryTag.user_id == user_id,
            MemoryTag.tag_name == tag_name,
        ).first()

        if tag:
            self.db.delete(tag)
            self.db.commit()
            return True

        return False

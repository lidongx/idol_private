"""
File Storage Service
Handles voice message and image file uploads
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException


class FileStorageService:
    """
    File storage service for voice and image messages

    MVP: Stores files locally in uploads/ directory
    Future: Migrate to S3/OSS for production
    """

    # Upload directory
    UPLOAD_DIR = Path("uploads")
    VOICE_DIR = UPLOAD_DIR / "voice"
    IMAGE_DIR = UPLOAD_DIR / "images"

    # Allowed file types
    ALLOWED_VOICE_EXTENSIONS = {".mp3", ".m4a", ".wav", ".aac", ".ogg"}
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Size limits (bytes)
    MAX_VOICE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB

    def __init__(self):
        """Initialize storage directories"""
        self._ensure_directories()

    def _ensure_directories(self):
        """Create upload directories if they don't exist"""
        self.VOICE_DIR.mkdir(parents=True, exist_ok=True)
        self.IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    async def save_voice_file(
        self,
        file: UploadFile,
        user_id: int
    ) -> Tuple[str, int]:
        """
        Save voice message file

        Args:
            file: Uploaded voice file
            user_id: User ID (for organizing files)

        Returns:
            Tuple of (file_url, duration_seconds)

        Raises:
            HTTPException: If file validation fails
        """
        # Validate file
        self._validate_voice_file(file)

        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
        file_path = self.VOICE_DIR / unique_filename

        # Save file
        try:
            content = await file.read()

            # Check file size
            if len(content) > self.MAX_VOICE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"语音文件过大，最大支持 {self.MAX_VOICE_SIZE // 1024 // 1024}MB"
                )

            with open(file_path, "wb") as f:
                f.write(content)

            # Get duration (simplified for MVP - return 0)
            # Future: Use pydub or ffprobe to get actual duration
            duration = self._get_audio_duration(file_path)

            # Return relative URL
            file_url = f"/uploads/voice/{unique_filename}"

            return file_url, duration

        except HTTPException:
            raise
        except Exception as e:
            print(f"[FileStorage] Voice save error: {e}")
            raise HTTPException(
                status_code=500,
                detail="文件保存失败"
            )

    async def save_image_file(
        self,
        file: UploadFile,
        user_id: int
    ) -> str:
        """
        Save image message file

        Args:
            file: Uploaded image file
            user_id: User ID

        Returns:
            file_url: URL to access the image

        Raises:
            HTTPException: If file validation fails
        """
        # Validate file
        self._validate_image_file(file)

        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
        file_path = self.IMAGE_DIR / unique_filename

        # Save file
        try:
            content = await file.read()

            # Check file size
            if len(content) > self.MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"图片文件过大，最大支持 {self.MAX_IMAGE_SIZE // 1024 // 1024}MB"
                )

            with open(file_path, "wb") as f:
                f.write(content)

            # Return relative URL
            file_url = f"/uploads/images/{unique_filename}"

            return file_url

        except HTTPException:
            raise
        except Exception as e:
            print(f"[FileStorage] Image save error: {e}")
            raise HTTPException(
                status_code=500,
                detail="文件保存失败"
            )

    def _validate_voice_file(self, file: UploadFile):
        """Validate voice file type"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名为空")

        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in self.ALLOWED_VOICE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的语音格式，支持: {', '.join(self.ALLOWED_VOICE_EXTENSIONS)}"
            )

    def _validate_image_file(self, file: UploadFile):
        """Validate image file type"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名为空")

        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片格式，支持: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            )

    def _get_audio_duration(self, file_path: Path) -> int:
        """
        Get audio file duration in seconds

        MVP: Returns 0 (duration calculation not critical for MVP)
        Future: Use pydub or ffprobe for accurate duration

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds (0 for MVP)
        """
        # TODO: Implement actual duration detection
        # Example with pydub:
        # from pydub import AudioSegment
        # audio = AudioSegment.from_file(file_path)
        # return int(audio.duration_seconds)

        return 0  # MVP: simplified

    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file by its URL

        Args:
            file_url: File URL (e.g., /uploads/voice/xxx.mp3)

        Returns:
            True if deleted successfully
        """
        try:
            # Convert URL to file path
            file_path = Path(file_url.lstrip("/"))

            if file_path.exists():
                file_path.unlink()
                return True

            return False

        except Exception as e:
            print(f"[FileStorage] Delete error: {e}")
            return False


# Global file storage instance
file_storage = FileStorageService()

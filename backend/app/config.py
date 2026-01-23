"""
Application Configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://idol_user:dev_password@localhost:5432/idol_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # SMS Service (MVP: console, Production: aliyun)
    SMS_PROVIDER: str = "console"
    ALIYUN_SMS_ACCESS_KEY_ID: str = ""
    ALIYUN_SMS_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = ""
    ALIYUN_SMS_TEMPLATE_CODE: str = ""

    # Application
    APP_NAME: str = "idol_private API"
    DEBUG: bool = True

    # AI Provider Configuration
    AI_PROVIDER: str = "ollama"  # Options: ollama, deepseek, claude

    # Ollama Configuration (Local AI)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2:7b"

    # Deepseek Configuration (Commercial API)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Claude Configuration (Commercial API)
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Payment Configuration
    # Alipay
    ALIPAY_APPID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""  # Path to private key file or key string
    ALIPAY_PUBLIC_KEY: str = ""   # Path to Alipay public key file or key string
    ALIPAY_SIGN_TYPE: str = "RSA2"
    ALIPAY_DEBUG: bool = True  # True for sandbox, False for production
    ALIPAY_RETURN_URL: str = "http://localhost:3000/payment/alipay/return"
    ALIPAY_NOTIFY_URL: str = "http://localhost:8000/api/v1/payments/alipay/notify"

    # WeChat Pay
    WECHAT_APPID: str = ""
    WECHAT_MCH_ID: str = ""       # Merchant ID
    WECHAT_API_KEY: str = ""      # API v2 key
    WECHAT_APICLIENT_CERT: str = ""  # Path to cert.pem
    WECHAT_APICLIENT_KEY: str = ""   # Path to key.pem
    WECHAT_NOTIFY_URL: str = "http://localhost:8000/api/v1/payments/wechat/notify"

    # Apple In-App Purchase
    APPLE_BUNDLE_ID: str = "com.idol.app"
    APPLE_SHARED_SECRET: str = ""  # App-specific shared secret from App Store Connect
    APPLE_SANDBOX_MODE: bool = True  # True for sandbox, False for production
    APPLE_VERIFY_URL_PRODUCTION: str = "https://buy.itunes.apple.com/verifyReceipt"
    APPLE_VERIFY_URL_SANDBOX: str = "https://sandbox.itunes.apple.com/verifyReceipt"
    APPLE_NOTIFICATION_URL: str = "http://localhost:8000/api/v1/payments/apple/notify"

    # Apple IAP Product IDs
    APPLE_PRODUCT_ID_MONTHLY: str = "com.idol.premium.monthly"
    APPLE_PRODUCT_ID_YEARLY: str = "com.idol.premium.yearly"

    # Google Play Billing
    GOOGLE_PLAY_PACKAGE_NAME: str = "com.idol.app"
    GOOGLE_PLAY_SERVICE_ACCOUNT_FILE: str = ""  # Path to service account JSON file
    GOOGLE_PLAY_NOTIFICATION_URL: str = "http://localhost:8000/api/v1/payments/google/notify"

    # Google Play Product IDs
    GOOGLE_PLAY_PRODUCT_ID_MONTHLY: str = "premium_monthly"
    GOOGLE_PLAY_PRODUCT_ID_YEARLY: str = "premium_yearly"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()

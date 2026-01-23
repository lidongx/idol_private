"""
Welcome message service
Generates time-based welcome messages from idols
"""
from datetime import datetime


def get_welcome_message(hour: int = None) -> str:
    """
    Generate welcome message based on time of day

    Args:
        hour: Hour of day (0-23). If None, uses current time.

    Returns:
        Welcome message string personalized to time of day
    """
    if hour is None:
        from datetime import datetime as dt
        hour = datetime.now().hour
    else:
        current_hour = hour

    if 6 <= current_hour < 12:
        # Morning (6:00-12:00)
        return "早上好呀~我是雪晴，很高兴遇见你。今天想聊些什么呢？"
    elif 12 <= current_hour < 18:
        # Afternoon (12:00-18:00)
        return "下午好~我是雪晴，你的专属陪伴者。有什么想和我分享的吗？"
    elif 18 <= current_hour < 24:
        # Evening (18:00-24:00)
        return "晚上好呀~我是雪晴。今天过得怎么样？来和我聊聊吧~"
    else:
        # Late night (0:00-6:00)
        return "这么晚还没睡呀？我是雪晴，陪你聊聊天吧~"

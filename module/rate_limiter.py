import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging

# Import the logger from logging_config
from conf.logging_config import logger

class RateLimiter:
    def __init__(self, max_requests: int, period: timedelta):
        self.max_requests = max_requests
        self.period = period
        self.requests = defaultdict(list)

    async def is_allowed(self, user_id: int) -> bool:
        now = datetime.now()
        if user_id in self.requests:
            self.requests[user_id] = [req for req in self.requests[user_id] if req > now - self.period]
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        return False

    def limit(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                user = update.effective_user
                if await self.is_allowed(user.id):
                    return await func(update, context, *args, **kwargs)
                else:
                    logger.warning(f"[요청 Quota 차단] {user.name}({user.id})")
                    await update.message.reply_text("요청이 너무 많아요. 잠시 뒤에 다시 물어보세요.")
            return wrapper
        return decorator
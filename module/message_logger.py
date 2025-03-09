from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from conf.logging_config import logger  # 상대 경로로 수정

def log_user_message(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        logger.info(f"[사용자 메세지] {user.username}({user.id}) : {update.message.text}")
        return await func(update, context, *args, **kwargs)
    return wrapper
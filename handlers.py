from datetime import timedelta
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler
from module.rate_limiter import RateLimiter
from module.message_logger import log_user_message
from module.archive import archive_url
from module.extract import extract_media_links
from conf.logging_config import logger  # 상대 경로로 수정
import asyncio
import pyshorteners
import validators
from conf.settings import QUOTA, QUOTA_TIME_SECOND

rate_limiter = RateLimiter(max_requests=QUOTA, period=timedelta(seconds=QUOTA_TIME_SECOND))

ASK_URL, PROCESS_URL = range(2)

@rate_limiter.limit()
@log_user_message
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

@rate_limiter.limit()
@log_user_message
async def ask_url(update: Update, context: ContextTypes.DEFAULT_TYPE, task_type: str) -> int:
    """Ask the user for the URL to archive or extract media links."""
    if task_type == 'archive':
        await update.message.reply_text("아카이빙할 URL 을 입력하세요.")
        context.user_data['task_type'] = 'archive'
    elif task_type == 'extract':
        await update.message.reply_text("미디어 링크를 추출할 URL을 입력하세요.")
        context.user_data['task_type'] = 'extract'
    return ASK_URL

@rate_limiter.limit()
@log_user_message
async def process_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the provided URL based on the task type."""
    url = update.message.text
    task_type = context.user_data.get('task_type')
    
    # Validate the URL
    if not validators.url(url):
        await update.message.reply_text("유효하지 않은 URL입니다. 다시 시도해주세요.")
        return ConversationHandler.END
    
    if task_type == 'archive':
        await update.message.reply_text("📝 아카이빙을 진행중입니다. 완료되면 알려드립니다.")
        # Create a background task to process the URL
        asyncio.create_task(handle_archive(update, context, url))
    elif task_type == 'extract':
        await update.message.reply_text("🔍 미디어 링크를 추출중입니다. 잠시만 기다려주세요.")
        # Create a background task to process the URL
        asyncio.create_task(handle_media_extraction(update, context, url))
    
    return ConversationHandler.END

async def handle_archive(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    """Handle the URL archiving in the background."""
    archive_link = await archive_url(url)
    if archive_link:
        # Shorten the archive URL
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(archive_link)
        await update.message.reply_text(f"아카이브 완료. 단축 URL: {short_url}")
    else:
        await update.message.reply_text("아카이빙 실패.. 나중에 다시 시도해주세요.")

async def handle_media_extraction(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
    decorated_line = "=" * 30
    media_links = await extract_media_links(url)
    if media_links:
        user = update.effective_user
        images = media_links['images']
        videos = media_links['videos']
        
        if images:
            msg = f"추출사용자 : {user.name}({user.id})\n추출 대상 url : {url}\n추출된 이미지 링크:\n" + "\n".join(images)
            logger.info(f"\n{decorated_line}\n{msg}\n{decorated_line}")
            await update.message.reply_text("추출된 이미지 🌆")
            media_group = [InputMediaPhoto(media=image) for image in images]
            try:
                await update.message.reply_media_group(media_group)
            except Exception as e:
                logger.error(f"Failed to send media group: {e}")
                await update.message.reply_text("직접 전송이 안 되는 이미지가 있어, URL 목록을 제공합니다:\n" + "\n".join(images))
        
        if videos:
            msg = f"추출사용자 : {user.name}({user.id})\n추출 대상 url : {url}\n추출된 비디오 링크:\n" + "\n".join(videos)
            logger.info(f"\n{decorated_line}\n{msg}\n{decorated_line}")
            await update.message.reply_text("추출된 동영상 🎥")
            for video in videos:
                await update.message.reply_text(video)
    else:
        await update.message.reply_text("미디어 링크 추출에 실패했습니다. 나중에 다시 시도해주세요.")
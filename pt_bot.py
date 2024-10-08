import asyncio
import inspect
import logging
import os

import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Application, ContextTypes, filters, CallbackQueryHandler, )

import pt_config
import pt_error
import pt_service
import pt_db
import pt_request
import pt_scheduler

application = Application.builder().token(pt_config.BOT_TOKEN).build()
logger = logging.getLogger("bot")
UNTRACK = range(1)
ADD_GOOD = range(1)

def check_user_reg(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Update):
                chat_id = str(arg.message.chat_id)
                user_id = str(arg.message.from_user.id)
                print(chat_id)
                break
        return func(*args, **kwargs)

    return wrapper


def _register_bot_command_handler():
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    add_good_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add)],
        fallbacks=[CommandHandler("cancel", cancel)],
        states={
            UNTRACK: [MessageHandler(filters.TEXT & (~filters.COMMAND), add_good)],
        },
    )

    application.add_handler(add_good_conv_handler)

    my_good_handler = CommandHandler("my", my_good)
    application.add_handler(my_good_handler)
# 使用 @check_user_reg 裝飾器修飾 start 函數
#check_user_reg 裝飾器：

#check_user_reg 是一個函數，包裝其他函數（如 start），用來檢查用戶是否在 registered_users 列表中。
#如果用戶已註冊，則會執行 start 函數；否則，它會發送一條訊息告訴用戶他們沒有註冊。

@check_user_reg
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f'''
            /my 顯示追蹤清單
            /clearall 清空全部追蹤清單
            /clear 刪除指定追蹤商品
            /add 後貼上momo商品連結可加入追蹤清單
            或是可以直接使用指令選單方便操作
            ====
            '''
    await update.message.reply_text(text=inspect.cleandoc(message))

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("貼上momo商品連結加入收藏\n輸入 /cancel 後放棄動作")
    return ADD_GOOD

async def my_good(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    #response = pt_db.find_user_sub_goods(user_id)
    #await update.message.reply_html(text=response.to_message(), disable_web_page_preview=True)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="已放棄動作")
    return ConversationHandler.END

async def add_good(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text
    urls_json = []
    urls_json.append(url)
    pt_scheduler.fetch_product_attributes(urls_json,user_id)

    return ConversationHandler.END

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    good_name = update.message.text
    #response = pt_service.clear_user_sub_goods(user_id, good_name)
    #await update.message.reply_text(text=response.to_message())
    return ConversationHandler.END


bot_event_loop = asyncio.new_event_loop()


def send(msg, chat_id):
    try:
        bot_event_loop.run_until_complete(application.bot.sendMessage(chat_id=chat_id, text=msg))
    except:
        logger.error("Send message and catch the exception.", exc_info=True)


_register_bot_command_handler()

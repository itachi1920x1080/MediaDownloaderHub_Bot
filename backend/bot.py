import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from services.downloader_service import download_video
from services.history_service import add_history, init_db
import logging

# កំណត់ Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()

# ទាញយក Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DONATE_QR_ID = os.getenv('DONATE_QR_FILE_ID')

# កំណត់ States សម្រាប់ ConversationHandler
WAITING_QUALITY = 1

# ក្តារចុច (Keyboard)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("ទាញយកវីដេអូ")],
        [KeyboardButton("ជំនួយ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"User {user.first_name} (ID: {user.id}) started the bot.")
    welcome_text = (
        "សួស្តី! ខ្ញុំជា Bot ទាញយកវីដេអូ។\n\n"
        "បញ្ជីបញ្ជា (Commands):\n"
        "/donate - ឧបត្ថម្ភការអភិវឌ្ឍ Bot របស់យើង\n"
        "/start - ចាប់ផ្តើមប្រើប្រាស់ Bot\n"
        "/cancel - បោះបង់ប្រតិបត្តិការកំពុងធ្វើ\n\n"
        "សូមជ្រើសរើសជម្រើសខាងក្រោម៖"
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Remove any accidental quotes from the string just in case
    clean_qr_id = DONATE_QR_ID.strip('\'"') if DONATE_QR_ID else None
    
    if clean_qr_id:
        try:
            await update.message.reply_photo(
                photo=clean_qr_id, 
                caption="សូមអរគុណសម្រាប់ការគាំទ្រដល់ការអភិវឌ្ឍ Bot របស់យើង!"
            )
        except Exception as e:
            logger.error(f"Error sending donate QR: {e}")
            await update.message.reply_text("មានបញ្ហាក្នុងការបង្ហាញ QR Code ឧបត្ថម្ភ។ សូមពិនិត្យមើល File ID នៅក្នុង .env ម្តងទៀត។")
    else:
        await update.message.reply_text("មិនមាន QR Code សម្រាប់ឧបត្ថម្ភនៅពេលនេះទេ។")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    
    logger.info(f"User {user.first_name} (ID: {user_id}) sent: {text}")
    
    if text == "ជំនួយ":
        help_text = (
            "ដើម្បីទាញយកវីដេអូ សូមផ្ញើ Link (TikTok, YouTube, ផ្សេងៗ) មកកាន់ខ្ញុំ។\n\n"
            "បញ្ជីបញ្ជា (Commands):\n"
            "/donate - ឧបត្ថម្ភការអភិវឌ្ឍ Bot របស់យើង\n"
            "/start - ចាប់ផ្តើមប្រើប្រាស់ Bot\n"
            "/cancel - បោះបង់ការទាញយក"
        )
        await update.message.reply_text(help_text)
        return ConversationHandler.END
    elif text == "ទាញយកវីដេអូ":
        await update.message.reply_text("សូម Copy Link វីដេអូ ហើយ Paste វានៅទីនេះ👇")
        return ConversationHandler.END
    
    # បើមិនមែនជា Button ទេ សន្មត់ថាជា Link
    url = text
    context.user_data['pending_url'] = url
    
    # បង្កើតប៊ូតុងជ្រើសរើសគុណភាព
    keyboard = [
        [InlineKeyboardButton("360p", callback_data='quality_360'),
         InlineKeyboardButton("720p", callback_data='quality_720'),
         InlineKeyboardButton("1080p", callback_data='quality_1080')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("សូមជ្រើសរើសគុណភាពដែលអ្នកចង់បាន៖", reply_markup=reply_markup)
    
    # ប្រាប់ ConversationHandler ថាកំពុងរង់ចាំការជ្រើសរើសគុណភាព
    return WAITING_QUALITY

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = user.id
    
    logger.info(f"User {user.first_name} (ID: {user_id}) clicked button: {query.data}")
    
    if query.data == 'download_btn':
        # ប្រាប់អ្នកប្រើប្រាស់ពីរបៀប Save វីដេអូចូលទូរស័ព្ទ
        await query.answer("សូមចុចលើវីដេអូ រួចជ្រើសរើស 'Save to Gallery' ឬ 'Save to Downloads' 📥", show_alert=True)
        return ConversationHandler.END
        
    if query.data.startswith('quality_'):
        quality = query.data.split('_')[1]
        await query.answer()
        
        url = context.user_data.get('pending_url')
        if not url:
            await query.edit_message_text("❌ រកមិនឃើញ Link ចាស់ទេ។ សូមផ្ញើ Link វីដេអូម្តងទៀត។")
            return ConversationHandler.END
            
        status_msg = await query.edit_message_text(f"⏳ កំពុងផ្តើមទាញយកគុណភាព {quality}p... សូមរង់ចាំ។")
        
        qr_msg = None
        if DONATE_QR_ID:
            try:
                qr_msg = await query.message.reply_photo(
                    photo=DONATE_QR_ID,
                    caption="🙏 ខណៈពេលរង់ចាំ សូមជួយគាំទ្រពួកយើងតាមរយៈ QR Code នេះ!"
                )
            except Exception as e:
                logger.error(f"Failed to send QR Code: {e}")
                
        state = {'percent': 0, 'speed': '', 'status': 'downloading'}
        
        # Task សម្រាប់ Update សារ (Progress Bar)
        async def update_progress():
            last_percent = -1
            while state['status'] == 'downloading':
                await asyncio.sleep(3)
                current_percent = int(state['percent'])
                if current_percent != last_percent:
                    bars = int(current_percent / 10)
                    progress_bar = '█' * bars + '░' * (10 - bars)
                    speed = state['speed']
                    text_msg = f"⏳ កំពុងទាញយកគុណភាព {quality}p...\n[{progress_bar}] {current_percent}%\nល្បឿន៖ {speed}"
                    try:
                        await status_msg.edit_text(text_msg)
                        last_percent = current_percent
                    except Exception:
                        pass
    
        progress_task = asyncio.create_task(update_progress())
        
        try:
            # កោះហៅសេវាកម្មទាញយកក្នុង Background មិនឱ្យគាំង Bot
            media_type, title, file_data = await asyncio.to_thread(download_video, url, state, quality)
            
            # កត់ត្រាប្រវត្តិទាញយក
            add_history(user_id, title, url)
            logger.info(f"User {user.first_name} (ID: {user_id}) successfully downloaded: {title} ({url})")
            
            state['status'] = 'finished'
            await progress_task
            
            await status_msg.edit_text("⏳ កំពុងបញ្ជូនឯកសារទៅកាន់ Telegram...\n(ដំណាក់កាលនេះអាចចំណាយពេលបន្តិច អាស្រ័យលើទំហំឯកសារ និងល្បឿន Internet របស់អ្នក)")
            
            # បង្កើតប៊ូតុង Download Inline
            keyboard = [[InlineKeyboardButton("📥 របៀប Save ឯកសារ", callback_data='download_btn')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if media_type == 'images':
                media_group = []
                for idx, path in enumerate(file_data):
                    caption = f"✅ ទាញយកជោគជ័យ!\nឈ្មោះ៖ {title}" if idx == 0 else ""
                    media_group.append(InputMediaPhoto(open(path, 'rb'), caption=caption))
                
                # Telegram អាចផ្ញើម្ដងបាន ១០ រូបភាព ដូច្នេះយើងត្រូវបំបែកវាបើមានច្រើន
                for i in range(0, len(media_group), 10):
                    batch = media_group[i:i+10]
                    await query.message.reply_media_group(media=batch, write_timeout=300)
                
                await query.message.reply_text("✅ រូបភាពទាំងអស់ត្រូវបានផ្ញើជោគជ័យ!", reply_markup=reply_markup)
                
                # លុបសារ "កំពុងដំណើរការ" ចោល
                await status_msg.delete()
                if qr_msg:
                    try:
                        await qr_msg.delete()
                    except:
                        pass
                
                # លុបរូបភាពចោលពីម៉ាស៊ីន
                for path in file_data:
                    if os.path.exists(path):
                        os.remove(path)
            else:
                file_path = file_data
                file_size = os.path.getsize(file_path)
                with open(file_path, 'rb') as video_file:
                    if file_size > 50 * 1024 * 1024: # ធំជាង 50MB
                        await query.message.reply_document(
                            document=video_file,
                            caption=f"✅ ទាញយកជោគជ័យ!\nឈ្មោះវីដេអូ៖ {title}\nគុណភាព៖ {quality}p",
                            reply_markup=reply_markup,
                            read_timeout=300,
                            write_timeout=300
                        )
                    else:
                        await query.message.reply_video(
                            video=video_file,
                            caption=f"✅ ទាញយកជោគជ័យ!\nឈ្មោះវីដេអូ៖ {title}\nគុណភាព៖ {quality}p",
                            reply_markup=reply_markup,
                            read_timeout=300,
                            write_timeout=300
                        )
                
                # លុបសារ "កំពុងដំណើរការ" ចោល
                await status_msg.delete()
                if qr_msg:
                    try:
                        await qr_msg.delete()
                    except:
                        pass
                
                # ៥. លុបឯកសារចេញពីម៉ាស៊ីនវិញដើម្បីសន្សំទំហំ Hard Disk
                if os.path.exists(file_path):
                    os.remove(file_path)
                
            # Clear pending url
            if 'pending_url' in context.user_data:
                del context.user_data['pending_url']
                
        except Exception as e:
            state['status'] = 'error'
            progress_task.cancel()
            await status_msg.edit_text(f"❌ ការទាញយកបរាជ័យ៖ {str(e)}")
            if qr_msg:
                try:
                    await qr_msg.delete()
                except:
                    pass
            
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ការទាញយកត្រូវបានលុបចោល។", reply_markup=get_main_keyboard())
    return ConversationHandler.END

async def get_photo_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # យក File ID ពីទំហំរូបភាពធំជាងគេ
    file_id = update.message.photo[-1].file_id
    await update.message.reply_text(f"នេះគឺជា File ID របស់អ្នក៖\n`{file_id}`", parse_mode='Markdown')

async def post_init(application):
    # បង្ហាញបញ្ជី Commands ទៅកាន់អ្នកប្រើប្រាស់ (Menu Button)
    # ដាក់ /donate មុនគេបង្អស់
    await application.bot.set_my_commands([
        ("donate", "ឧបត្ថម្ភការអភិវឌ្ឍ Bot របស់យើង"),
        ("start", "ចាប់ផ្តើមប្រើប្រាស់ Bot"),
        ("cancel", "បោះបង់ប្រតិបត្តិការកំពុងធ្វើ")
    ])

if __name__ == '__main__':
    if not TOKEN:
        print("កំហុស៖ មិនឃើញមាន TELEGRAM_BOT_TOKEN ក្នុងឯកសារ .env ទេ។")
        exit()
        
    # បង្កើត Database បើមិនទាន់មាន
    init_db()
        
    # Force HTTP/1.1 to fix Telegram Bad Gateway (502) errors
    from telegram.request import HTTPXRequest
    t_request = HTTPXRequest(http_version="1.1")
    
    app = ApplicationBuilder().token(TOKEN).request(t_request).post_init(post_init).build()
    
    # បង្កើត ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)],
        states={
            WAITING_QUALITY: [
                CallbackQueryHandler(button_callback, pattern='^quality_'),
                # បើអ្នកប្រើប្រាស់ផ្ញើ Link ថ្មី ខណៈពេលកំពុងរង់ចាំឱ្យជ្រើសរើសគុណភាព វាគ្រាន់តែចាប់ផ្តើមសារថ្មីម្តងទៀត
                MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
            ],
        },
        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('cancel', cancel),
            CommandHandler('donate', donate),
            CallbackQueryHandler(button_callback, pattern='^download_btn$') # in case they click it anytime
        ],
        per_message=False # បិទ Warning របស់ PTB កុំឱ្យរំខាន
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("donate", donate))
    app.add_handler(conv_handler)
    
    # Handler for download_btn outside conversation (just in case they click old buttons)
    app.add_handler(CallbackQueryHandler(button_callback, pattern='^download_btn$'))
    
    # Handler សម្រាប់ទទួលបាន File ID ពីរូបភាព
    app.add_handler(MessageHandler(filters.PHOTO, get_photo_file_id))
    
    print("Bot កំពុងដំណើរការ...")
    app.run_polling()
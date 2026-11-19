import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ==============================================================================
# 1. تنظیمات اصلی ربات (فقط این دو خط را پر کنید)
# ==============================================================================
BOT_TOKEN = "توکن_ربات_خود_را_اینجا_قرار_دهید"       # توکن دریافتی از @BotFather
MINIAPP_URL = "آدرس_لینک_مینی_اپ_خود_را_اینجا_بگذارید" # لینک HTTPS گیت‌هاب پیج شما
ADMIN_CHAT_ID = 9216569805                         # شناسه عددی شما (ثبت شده)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==============================================================================
# 2. کیبورد باز کردن مینی‌اپ (مخصوص روش دوم: Telegram.WebApp.sendData)
# ==============================================================================
def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 باز کردن پنل مدیریت GSMFIX",
                    web_app=WebAppInfo(url=MINIAPP_URL)
                )
            ]
        ],
        resize_keyboard=True
    )


# ==============================================================================
# 3. دستور /start برای نمایش دکمه مینی‌اپ
# ==============================================================================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 سلام! به ربات هوشمند مرکز تعمیرات **GSMFIX** خوش آمدید.\n\n"
        "برای ثبت پذیرش، مدیریت بدهکاران و ارسال قبض‌ها روی دکمه زیر بزنید:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


# ==============================================================================
# 4. دریافت خودکار داده‌ها از مینی‌اپ (قبض تعمیرات، بدهکاران و تست اتصال)
# ==============================================================================
@dp.message(F.web_app_data)
async def handle_gsmfix_webapp_data(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        action = data.get("act", "")

        # الف) دریافت گزارش از بخش بدهکاران
        if action == "DEBTOR_REPORT":
            total = int(data.get("total", 0))
            paid = int(data.get("paid", 0))
            rem = int(data.get("rem", 0))
            status_text = "✅ تسویه کامل" if rem <= 0 else "🔴 بدهکار"

            text = (
                f"📒 **گزارش حساب دفتری / بدهکاران GSMFIX**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **مشتری:** {data.get('cust', '-')}\n"
                f"📞 **تلفن:** `{data.get('phone', '-')}`\n"
                f"📌 **بابت:** {data.get('reason', '-')}\n"
                f"💰 **مبلغ کل:** {total:,} تومان\n"
                f"✅ **پرداخت‌شده:** {paid:,} تومان\n"
                f"💳 **مانده بدهی:** **{rem:,} تومان**\n"
                f"📅 **سررسید:** {data.get('due', '-')}\n"
                f"📊 **وضعیت:** {status_text}"
            )
            await message.answer(text, parse_mode="Markdown")

        # ب) دریافت قبض پذیرش یا تغییر وضعیت تعمیرات (سخت‌افزار و نرم‌افزار)
        elif action in ["ORDER_RECEIPT", "NEW_ORDER_CREATED", "ORDER_STATUS_UPDATED"]:
            dept = "🔧 سخت‌افزار" if data.get("cat") == "HW" else "💻 نرم‌افزار"
            services = "، ".join(data.get("srvs", [])) or "-"
            cost = int(data.get("cost", 0))

            text = (
                f"🧾 **قبض پذیرش دیجیتال GSMFIX**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🔖 **کد پیگیری:** `{data.get('code', '-')}`\n"
                f"📂 **بخش:** {dept}\n"
                f"📱 **دستگاه:** {data.get('model', '-')}\n"
                f"👤 **مشتری:** {data.get('cust', '-')}\n"
                f"📞 **تماس:** `{data.get('phone', '-')}`\n"
                f"👨‍🔧 **مسئول:** {data.get('tech', '-')}\n"
                f"⚙️ **وضعیت:** {data.get('stat', '-')}\n"
                f"🛠️ **خدمات:** {services}\n"
                f"📅 **ورود / تحویل:** {data.get('in_d', '-')} ⬅️ {data.get('out_d', '-')}\n"
                f"💰 **برآورد هزینه:** **{cost:,} تومان**"
            )
            await message.answer(text, parse_mode="Markdown")

        # پ) تست اتصال ربات
        elif action == "PING_TEST":
            await message.answer(
                f"✅ **اتصال برقرار است!**\n"
                f"شناسه مقصد: `{data.get('chat_id', ADMIN_CHAT_ID)}`\n"
                f"تعداد کل پرونده‌های ثبت‌شده: `{data.get('total', 0)}`",
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Error parsing web_app_data: {e}")
        await message.answer("❌ خطا در پردازش اطلاعات دریافتی از مینی‌اپ.")


# ==============================================================================
# 5. اجرای ربات
# ==============================================================================
async def main():
    print("🤖 ربات GSMFIX با پشتیبانی کامل از بخش بدهکاران و قبض‌ها روشن شد...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
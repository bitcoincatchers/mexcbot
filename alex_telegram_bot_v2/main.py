#!/usr/bin/env python3
"""
Alex's Telegram Bot - $50 to $500 Crypto Trading Challenge
Updated version with smart UID detection and new messaging flow
"""

import logging
import re
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import hashlib
import hmac
import time
import json
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        # Bot Configuration
        self.TELEGRAM_TOKEN = "8016598513:AAFtYbJD6vOXpIH9t8wu_-nSfBJmSn2KQNk"

        # MEXC API Configuration
        self.MEXC_API_KEY = "mx0vgl6Q1sImSUitga"
        self.MEXC_SECRET = "b79a8e0f6a4b4730a0e7e198e5b5e110"
        self.MEXC_BASE_URL = "https://api.mexc.com"

        # VIP Group Configuration
        self.VIP_GROUP_LINK = "https://t.me/+S4YxyCi0aEU3ZTA0"

        # UID Pattern for smart detection (8 digits)
        self.UID_PATTERN = re.compile(r'\b(?:uid\s*)?([0-9]{8})\b', re.IGNORECASE)

        # Verified users storage (in production, use a database)
        self.verified_users = set()

        # Welcome message
        self.WELCOME_MESSAGE = """🚀 ¡Bienvenido al reto de 50$ a 500$ con Cripto Trading! 🚀

Antes de empezar necesitaremos verificar tu UID de mexc

Por favor asegurate de registrarte en MEXC con este enlace:
https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc

Una vez registrado , haz click la parte superior derecha , en el icono de tu cuenta.
Esta te mostrará tu correo electrónico y tu número de usuario UID.

Por favor haz click aquí /verify o escribe /verify
Y pega tu numero de UID que se forma por 8 dígitos."""

        self.SUCCESS_MESSAGE = """Perfecto! , hemos verificado tu numero de UID y estás registrado correctamente, puedes unirte al reto 50$ - 500$ haciendo click aquí ( {} )"""

        self.FAILURE_MESSAGE = """Vaya! , parece que no encontramos tu UID de usuario.
Por favor asegurate de registrarte en MEXC con este enlace:
https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc

Una vez registrado , haz click la parte superior derecha , en el icono de tu cuenta.
Esta te mostrará tu correo electrónico y tu número de usuario UID.

Por favor haz click aquí /verify o escribe /verify
Y pega tu numero de UID que se forma por 8 dígitos.

Si tienes algún problema contacta con alex directamente haciendo click aquí
@alex.worksout"""

    def generate_mexc_signature(self, query_string: str) -> str:
        """Generate MEXC API signature"""
        return hmac.new(
            self.MEXC_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def verify_mexc_uid(self, uid: str) -> bool:
        """Verify UID with MEXC API"""
        try:
            timestamp = str(int(time.time() * 1000))
            query_string = f"timestamp={timestamp}"
            signature = self.generate_mexc_signature(query_string)

            headers = {
                'X-MEXC-APIKEY': self.MEXC_API_KEY,
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                url = f"{self.MEXC_BASE_URL}/api/v3/account"
                params = {
                    'timestamp': timestamp,
                    'signature': signature
                }

                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return len(uid) == 8 and uid.isdigit()
                    return False

        except Exception as e:
            logger.error(f"Error verifying UID {uid}: {e}")
            return False

    def extract_uid_from_message(self, text: str) -> Optional[str]:
        """Extract UID from message using smart detection"""
        match = self.UID_PATTERN.search(text)
        if match:
            return match.group(1)
        return None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")

        keyboard = [
            [InlineKeyboardButton("🔍 Verificar UID", callback_data="verify_uid")],
            [InlineKeyboardButton("📞 Contactar Alex", url="https://t.me/alex.worksout")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            self.WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /verify command"""
        await update.message.reply_text(
            "Por favor, envía tu UID de MEXC (8 dígitos).\n\n"
            "Puedes enviarlo de cualquiera de estas formas:\n"
            "• Solo el número: 12345678\n"
            "• Con texto: UID 12345678\n"
            "• En cualquier mensaje que contenga tu UID de 8 dígitos"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all text messages with smart UID detection"""
        user = update.effective_user
        message_text = update.message.text

        logger.info(f"Message from {user.id} ({user.username}): {message_text}")

        uid = self.extract_uid_from_message(message_text)

        if uid:
            await self.process_uid_verification(update, context, uid)
        else:
            await update.message.reply_text(
                "No he detectado un UID válido en tu mensaje. 🤔\n\n"
                "Recuerda que el UID debe tener exactamente 8 dígitos.\n\n"
                "Ejemplos válidos:\n"
                "• 12345678\n"
                "• UID 12345678\n"
                "• Mi UID es 12345678\n\n"
                "¿Necesitas ayuda? Usa /verify para más información."
            )

    async def process_uid_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE, uid: str) -> None:
        """Process UID verification"""
        user = update.effective_user

        verification_message = await update.message.reply_text(
            f"🔍 Verificando UID: {uid}...\n"
            "Por favor espera un momento."
        )

        try:
            is_valid = await self.verify_mexc_uid(uid)

            if is_valid:
                self.verified_users.add(user.id)

                keyboard = [
                    [InlineKeyboardButton("🎯 Unirse al Reto 50$ - 500$", url=self.VIP_GROUP_LINK)],
                    [InlineKeyboardButton("📞 Contactar Alex", url="https://t.me/alex.worksout")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await verification_message.edit_text(
                    self.SUCCESS_MESSAGE.format(self.VIP_GROUP_LINK),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )

                logger.info(f"UID {uid} verified successfully for user {user.id}")

            else:
                keyboard = [
                    [InlineKeyboardButton("📝 Registrarse en MEXC", url="https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc")],
                    [InlineKeyboardButton("🔍 Intentar de nuevo", callback_data="verify_uid")],
                    [InlineKeyboardButton("📞 Contactar Alex", url="https://t.me/alex.worksout")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await verification_message.edit_text(
                    self.FAILURE_MESSAGE,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )

                logger.warning(f"UID {uid} verification failed for user {user.id}")

        except Exception as e:
            logger.error(f"Error during UID verification: {e}")
            await verification_message.edit_text(
                "❌ Error durante la verificación. Por favor intenta de nuevo más tarde.\n\n"
                "Si el problema persiste, contacta con @alex.worksout"
            )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        if query.data == "verify_uid":
            await query.edit_message_text(
                "Por favor, envía tu UID de MEXC (8 dígitos).\n\n"
                "Puedes enviarlo de cualquiera de estas formas:\n"
                "• Solo el número: 12345678\n"
                "• Con texto: UID 12345678\n"
                "• En cualquier mensaje que contenga tu UID de 8 dígitos"
            )

    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("verify", self.verify_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        from telegram.ext import CallbackQueryHandler
        application.add_handler(CallbackQueryHandler(self.button_callback))

        logger.info("Starting Alex's Telegram Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

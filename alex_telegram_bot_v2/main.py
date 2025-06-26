import os
import asyncio
import logging
import hashlib
import hmac
import time
import json
import re
from urllib.parse import urlencode
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración con tus credenciales
TELEGRAM_TOKEN = "8016598513:AAFtYbJD6vOXpIH9t8wu_-nSfBJmSn2KQNk"
MEXC_API_KEY = "mx0vgl6Q1sImSUitga"
MEXC_SECRET_KEY = "b79a8e0f6a4b4730a0e7e198e5b5e110"
VIP_GROUP_ID = "https://t.me/+S4YxyCi0aEU3ZTA0"

class MEXCAPIClient:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.mexc.com"
        self.session = None
        self.referral_uids = []
        
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    def generate_signature(self, params: str) -> str:
        return hmac.new(
            self.secret_key.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_referral_uids(self):
        try:
            await self.create_session()
            
            endpoint = "/api/v3/rebate/taxQuery"
            params = {
                'recvWindow': 5000,
                'timestamp': int(time.time() * 1000)
            }
            
            query_string = urlencode(params)
            signature = self.generate_signature(query_string)
            params['signature'] = signature
            
            headers = {
                'X-MEXC-APIKEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Datos de rebate obtenidos correctamente")
                    
                    uids = []
                    if isinstance(data, dict) and 'data' in data:
                        for item in data['data']:
                            if isinstance(item, dict) and 'uid' in item:
                                uids.append(str(item['uid']))
                    
                    self.referral_uids = list(set(uids))
                    logger.info(f"UIDs de referidos encontrados: {len(self.referral_uids)} UIDs")
                    return self.referral_uids
                else:
                    logger.error(f"Error al obtener datos de rebate: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error al obtener UIDs de referidos: {e}")
            return []
        finally:
            if self.session:
                await self.session.close()
                self.session = None
    
    async def verify_uid(self, uid: str) -> bool:
        if not self.referral_uids:
            await self.get_referral_uids()
        return str(uid) in self.referral_uids

class TelegramBot:
    def __init__(self, token: str, mexc_client: MEXCAPIClient, vip_group_id: str):
        self.token = token
        self.mexc_client = mexc_client
        self.vip_group_id = vip_group_id
        self.uid_pattern = re.compile(r'\b\d{8}\b')
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = """🚀 ¡Bienvenido al reto de 50$ a 500$ con Cripto Trading! 🚀

Antes de empezar necesitaremos verificar tu UID de mexc

Por favor asegurate de registrarte en MEXC con este enlace:
https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc

Una vez registrado , haz click la parte superior derecha , en el icono de tu cuenta.
Esta te mostrará tu correo electrónico y tu número de usuario UID.

Por favor haz click aquí /verify o escribe /verify
Y pega tu numero de UID que se forma por 8 dígitos."""
        
        keyboard = [
            [InlineKeyboardButton("🔐 /verify", callback_data="verify_uid")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup
        )
    
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        verification_message = """🔍 **Verificación de UID de MEXC**

Por favor envía tu UID de MEXC (8 dígitos).

📋 **¿Cómo encontrar tu UID?**
1. Abre la app o web de MEXC
2. Ve a tu perfil/cuenta  
3. Busca "UID" o "User ID"
4. Copia los 8 números

📱 **Envía tu UID** (ejemplo: 12345678)"""
        
        await update.message.reply_text(verification_message)
        context.user_data['awaiting_uid'] = True
    
    async def verify_uid_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        verification_message = """🔍 **Verificación de UID de MEXC**

Por favor envía tu UID de MEXC (8 dígitos).

📋 **¿Cómo encontrar tu UID?**
1. Abre la app o web de MEXC
2. Ve a tu perfil/cuenta
3. Busca "UID" o "User ID"  
4. Copia los 8 números

📱 **Envía tu UID** (ejemplo: 12345678)"""
        
        await query.edit_message_text(verification_message)
        context.user_data['awaiting_uid'] = True
    
    def extract_uid_from_message(self, text: str) -> str:
        matches = self.uid_pattern.findall(text)
        return matches[0] if matches else None
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        uid = self.extract_uid_from_message(text)
        
        if uid:
            await self.verify_uid_process(update, context, uid)
        elif context.user_data.get('awaiting_uid', False):
            await update.message.reply_text(
                "❌ **UID inválido**\n\nPor favor, envía exactamente 8 dígitos. Ejemplo: 12345678"
            )
    
    async def verify_uid_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE, uid: str):
        verification_msg = await update.message.reply_text(
            "🔄 **Verificando tu UID...**\n\nEstoy comprobando si eres un referido de Alex en MEXC."
        )
        
        try:
            is_verified = await self.mexc_client.verify_uid(uid)
            
            if is_verified:
                success_message = f"""✅ **Perfecto!** , hemos verificado tu numero de UID y estás registrado correctamente, puedes unirte al reto 50$ - 500$ haciendo click aquí:

👉 {self.vip_group_id}

🚀 **¡Bienvenido al reto!**"""
                
                keyboard = [
                    [InlineKeyboardButton("🎯 Unirse al Reto 50$ - 500$", url=self.vip_group_id)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await verification_msg.edit_text(success_message, reply_markup=reply_markup)
                logger.info(f"Usuario verificado: {update.effective_user.id}, UID: {uid}")
                
            else:
                fail_message = """❌ **Vaya!** , parece que no encontramos tu UID de usuario.

Por favor asegurate de registrarte en MEXC con este enlace:
https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc

Una vez registrado , haz click la parte superior derecha , en el icono de tu cuenta.
Esta te mostrará tu correo electrónico y tu número de usuario UID.

Por favor haz click aquí /verify o escribe /verify
Y pega tu numero de UID que se forma por 8 dígitos.

Si tienes algún problema contacta con alex directamente haciendo click aquí:
@alex.worksout"""
                
                keyboard = [
                    [InlineKeyboardButton("📝 Registrarse en MEXC", url="https://www.mexc.com/es/acquisition/custom-sign-up?shareCode=mexc-15AJc")],
                    [InlineKeyboardButton("🔄 /verify", callback_data="verify_uid")],
                    [InlineKeyboardButton("💬 Contactar Alex", url="https://t.me/alex.worksout")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await verification_msg.edit_text(fail_message, reply_markup=reply_markup)
                logger.info(f"Usuario NO verificado: {update.effective_user.id}, UID: {uid}")
                
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            await verification_msg.edit_text(
                "❌ **Error de Verificación**\n\nHubo un problema técnico. Por favor, inténtalo de nuevo en unos minutos."
            )
        
        context.user_data['awaiting_uid'] = False

async def main():
    logger.info("🚀 Iniciando bot del reto 50$ - 500$ de Alex...")
    
    # Crear cliente MEXC
    mexc_client = MEXCAPIClient(MEXC_API_KEY, MEXC_SECRET_KEY)
    
    # Cargar UIDs de referidos al inicio
    logger.info("📡 Cargando UIDs de referidos...")
    await mexc_client.get_referral_uids()
    
    # Crear bot de Telegram
    bot = TelegramBot(TELEGRAM_TOKEN, mexc_client, VIP_GROUP_ID)
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Añadir handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("verify", bot.verify_command))
    application.add_handler(CallbackQueryHandler(bot.verify_uid_callback, pattern="verify_uid"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    logger.info("✅ Bot del reto iniciado correctamente. Esperando mensajes...")
    
    # Iniciar bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

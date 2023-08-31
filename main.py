import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import qrcode
import io
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np

load_dotenv()  # Load environment variables from .env file

# Configure your bot token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def qr(ctx, *, prompt):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(prompt)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Send the QR code image to Discord
    qr_img_bytes = io.BytesIO()
    qr_img.save(qr_img_bytes, format='PNG')
    qr_img_bytes.seek(0)

    qr_data = discord.File(qr_img_bytes, filename="qr_code.png")
    await ctx.send(file=qr_data)

@bot.command()
async def scan(ctx):
    # Check if there are any attachments
    if not ctx.message.attachments:
        await ctx.send("No image attachment found.")
        return

    # Get the first attachment (assuming only one image is uploaded)
    image_attachment = ctx.message.attachments[0]

    # Download the image
    async with ctx.typing():
        img_data = await image_attachment.read()

    # Decode QR code from image
    img_array = np.frombuffer(img_data, np.uint8)
    img = Image.open(io.BytesIO(img_array))

    decoded_objects = decode(img)
    
    # Extract and send QR code content
    if decoded_objects:
        qr_content = decoded_objects[0].data.decode('utf-8')
        await ctx.send(f"QR Code content: {qr_content}")
    else:
        await ctx.send("No QR code found in the image.")


bot.run(TOKEN)

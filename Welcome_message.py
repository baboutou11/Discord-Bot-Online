import os
import io
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# --- 1. BOT SETUP & CONFIGURATION ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Paste your friend's welcome channel ID and bot token below
WELCOME_CHANNEL_ID = 1515351921169273047


# --- 2. IMAGE COORDINATES & SETTINGS (Scaled for 800 x 400) ---
BG_PATH = "card_background.png"
AVATAR_SIZE = (56, 56)  # Fits neatly inside the white speech bubble
AVATAR_POS = (387, 222)  # Top-left corner inside the bubble
TEXT_POS = (660, 382)  # Centered directly under "welcome to the club!"
TEXT_COLOR = (255, 255, 255)  # Pure White


async def create_welcome_card(member):
  # Load background
  background = Image.open(BG_PATH).convert("RGBA")

  # Fetch and process member's Discord avatar
  try:
    avatar_asset = member.display_avatar.with_size(512)
    avatar_bytes = await avatar_asset.read()
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_img = avatar_img.resize(AVATAR_SIZE, Image.Resampling.LANCZOS)

    # Create circle mask
    mask = Image.new("L", AVATAR_SIZE, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, AVATAR_SIZE[0], AVATAR_SIZE[1]), fill=255)
    avatar_img.putalpha(mask)

    # Paste avatar onto background
    background.paste(avatar_img, AVATAR_POS, avatar_img)
  except Exception as e:
    print(f"Failed to process avatar: {e}")

  # Draw member's username using comic_sans_blod.ttf
  draw = ImageDraw.Draw(background)
  custom_font = ImageFont.truetype("comic_sans_blod.ttf", 20)

  draw.text(
      TEXT_POS,
      member.display_name,
      fill=TEXT_COLOR,
      font=custom_font,
      anchor="mm",
      stroke_width=2,
      stroke_fill=(0, 0, 0),
  )

  # Save to buffer so Discord can send it
  buffer = io.BytesIO()
  background.save(buffer, format="PNG")
  buffer.seek(0)
  return discord.File(fp=buffer, filename="welcome_card.png")


# --- 3. BOT EVENTS & COMMANDS ---
@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}!")


@bot.event
async def on_member_join(member: discord.Member):
  channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
  if channel:
    file = await create_welcome_card(member)
    await channel.send(
        content=f"Welcome to the club, {member.mention}!",
        file=file,
    )


@bot.command()
async def test(ctx):
  """Type !test in Discord to check the card layout!"""
  file = await create_welcome_card(ctx.author)
  await ctx.send(
      content=f"Test welcome card for {ctx.author.mention}:",
      file=file,
  )


# --- 4. START THE BOT ---
bot.run(os.getenv("DISCORD_TOKEN"))

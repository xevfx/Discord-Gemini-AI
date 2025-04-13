import os
os.system("pip install -r requirements.txt")
import asyncio
import logging
import tracemalloc

import google.generativeai as genai
import discord
from discord import app_commands
from discord.ext import commands

tracemalloc.start()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#token = os.getenv("token")
gemini_api_key = "key"

genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.all()
xevfx = commands.Bot(command_prefix="?", intents=intents)

@xevfx.event
async def on_ready():
    print(f"Logged in as {xevfx.user}")
    await xevfx.tree.sync()

@xevfx.tree.command(name="gemini", description="Ask Gemini anything!")
@app_commands.describe(prompt="Enter prompt")
async def geminicmd(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    try:
        generation_config = {
            'temperature': 0.7,
            'max_output_tokens': 1000,
            'top_p': 0.95,
            'top_k': 40,
        }

        response = await asyncio.to_thread(
            gemini_model.generate_content,
            prompt,
            generation_config=generation_config
        )
        response_text = response.text if hasattr(response, 'text') else str(response)

        if len(response_text) <= 1900:
            await interaction.followup.send(response_text)
        else:
            chunks = [response_text[i:i+1900] for i in range(0, len(response_text), 1900)]
            for i, chunk in enumerate(chunks):
                await interaction.followup.send(f"{chunk}\n(Part {i+1}/{len(chunks)})")

    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@xevfx.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Slow down! You can use this command again in {error.retry_after:.1f} seconds.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"An error occurred: {str(error)}",
            ephemeral=True
        )

#if __name__ == "__main__":
    
xevfx.run("token")
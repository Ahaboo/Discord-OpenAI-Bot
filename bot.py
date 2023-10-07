import discord
import openai
from discord.ext import commands
from dataclasses import dataclass

# Replace "Your_Key" with your actual bot token and OpenAI API key
BOT_TOKEN = "Your_Bot_Token"
OPENAI_API_KEY = "Your_OpenAI_API_Key"

# Replace with the channel ID where you want the bot to operate
CHANNEL_ID = # Enter your channel ID Number

# Maximum session time in minutes for the bot to be active
MAX_SESSION_TIME_MINUTES = 45

# Context that will be added to user prompts
context = "Please enhance the user's input by adding the missing categories (Textures, Quality, Lighting, Artistic Style, Camera) to create a detailed prompt for DALL·E, using popular choices for image generation for each of these categories.Here are the constraints for the output:1) Textures can be “Detailed”,“Award-Winning Art”, “Photorealistic” ,“Unreal Engine” Quality can be “4K/8K”,“15mm wide-angle lens” Award-Winning”2) Lighting can be “Cinematic Lighting”,“Studio Lighting”3) Artistic Style can be one of, Salvador Dali","Norman Rockwell","Banksy (Street Art)","Tim Burton, Camera)4) Camera can be any type of camera shots5) Do not include any words that mention AI generation or that include DALLEOutput should be a single sentence with the updated promptHere is an example input:an alien two dogsHere is an example output:an alien two dogs, Detailed Textures, 4K/8K Quality, Cinematic Lighting, Artistic Style Salvador Dali, 15mm wide-angle lens Camera"

# Define a data class to store session information
@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

# Create a Discord bot instance
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Initialize a session
session = Session()

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(
        "Hello! I am a bot used to create prompts and generate images using OpenAI, I have two commands, !createPrompt (prompt) to improve your prompt for AI Image Generation, Type !generate (prompt) to generate images with your improved prompt!"
    )
    # Send a welcome message to the specified channel
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send(
        "Hello! I am a bot used to create prompts and generate images using OpenAI, I have two commands, !createPrompt (prompt) to improve your prompt for AI Image Generation, Type !generate (prompt) to generate images with your improved prompt!"
    )

# Command to create an improved prompt
@bot.command()
async def createPrompt(ctx, *, prompt=None):
    try:
        if prompt is None:
            await ctx.send("Please provide a prompt for AI image generation.")
            return

        if len(prompt) < 4:
            await ctx.send("Please provide a valid prompt with at least 4 characters.")
            return

        prompt_with_context = f"Context: {context}\nUser Prompt: {prompt}"

        # Send the user's prompt to ChatGPT-3 using the chat/completions endpoint
        newPrompt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the chat model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_with_context},
            ],
        )

        # Get the generated response from ChatGPT-3
        bot_response = newPrompt.choices[0].message["content"].strip()

        # Print the bot's response
        print("Bot's Response:", bot_response)

        # Send the generated response back to the user
        await ctx.send(bot_response)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Command to generate an image based on a prompt
@bot.command()
async def generate(ctx, *, prompt=None):
    try:
        if prompt is None:
            await ctx.send("Please provide a prompt for AI image generation.")
            return

        # Check if the prompt is empty or too short
        if len(prompt) < 16:
            await ctx.send("Please provide a valid prompt with at least 16 characters.")
            return

        # Send the user's prompt to DALL·E 2 to generate an image
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")

        # Get the generated image URL from the response
        image_url = response["data"][0]["url"]

        # Send the generated image URL back to the user
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot with the provided token
bot.run(BOT_TOKEN)
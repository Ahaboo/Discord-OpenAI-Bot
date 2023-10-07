import discord
import openai
import random
from discord.ext import commands
from dataclasses import dataclass

# Replace "Your_Key" with your actual bot token and OpenAI API key
BOT_TOKEN = "Your_Bot_Token"
OPENAI_API_KEY = "Your_OpenAI_API_Key"

# Replace with the channel ID where you want the bot to operate
CHANNEL_ID = # Enter your channel ID Number

# Replace with the channel ID where you want the bot to operate
CHANNEL_ID = 1160042424110944279

# Maximum session time in minutes for the bot to be active
MAX_SESSION_TIME_MINUTES = 45

# Define arrays of categories
artistic_modifier = ["Salvador Dali", "Norman Rockwell", "Banksy (Street Art)", "Tim Burton", "Takashi Murakami","Van Gogh","Warhol" ]
art_styles = ["Digital Art", "Steampunk Art", "Cyberpunk Art", "ukiyo-e Art", "Deco Art","Vector Art","Low Poly Art","Glitchcore Art","Bauhaus Art","Modern Art","Coloring Book","Line Art","Vapowrwave Art","Ball-point Pen Art","pencil sketch/pencil drawing","anime","grafitti art","cartoon art","stock art","3d art","watercolor art"]
art_modifiers = ["detailed", "Award-Winning Art", "Trending on ArtStation", "Photorealistic", "Unreal Engine","Fanart"]
photorealistic_modifiers = ["4k/8k", "15mm wide-angle lens", "35mm lens", "85 mm lens", "200 mm lens", "Bokeh","Award-Winning","Tilt-Shift Photography","Cinematic Movie Photograph","Macro"]
lighting_modifiers = ["Cinematic Lighting", "At/During Golden Hour", "Golden Hour Sunlight", "Ambient Lighting","Studio Lighting","Lens Flare"]


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
    # Send a welcome message to the specified channel
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send(
        "Hello! I am a bot used to create prompts and generate images using OpenAI, I have one command, !generate (prompt) that improves your prompt using prompt engineering and then generates the image using DALLE2"
    )

@bot.command()
async def generate(ctx, *, prompt=None):
    try:
        if prompt is None:
            await ctx.send("Please provide a prompt for AI image generation.")
            return

        # Check if the prompt is empty or too short
        if len(prompt) < 4:
            await ctx.send("Please provide a valid prompt with at least 4 characters.")
            return

        # Split the user's prompt into words
        user_prompt_words = prompt.split()

        # Initialize variables to store selected categories
        selected_artistic_modifier = None
        selected_art_style = None
        selected_art_modifier = None
        selected_photorealistic_modifier = None
        selected_lighting_modifier = None

        # Initialize a variable to store the user's subject
        user_subject = ""

        # Check the user's prompt for category mentions and set the selected categories
        for word in user_prompt_words:
            found = False  # Track whether a category has been found for the current word
            for modifier in artistic_modifier:
                if word.lower() in modifier.lower():
                    selected_artistic_modifier = modifier
                    found = True
                    break  # Exit the inner loop if a match is found
            if found:
                continue  # Skip the rest of the loop for this word

            for style in art_styles:
                if word.lower() in style.lower():
                    selected_art_style = style
                    found = True
                    break

            for modifier in art_modifiers:
                if word.lower() in modifier.lower():
                    selected_art_modifier = modifier
                    found = True
                    break

            for modifier in photorealistic_modifiers:
                if word.lower() in modifier.lower():
                    selected_photorealistic_modifier = modifier
                    found = True
                    break

            for modifier in lighting_modifiers:
                if word.lower() in modifier.lower():
                    selected_lighting_modifier = modifier
                    found = True
                    break

            if not found:
                # If no match is found for a word, add it to the user's subject
                user_subject += word + " "

        # Remove trailing whitespace from the user's subject
        user_subject = user_subject.strip()

        # If any category is not mentioned in the user's prompt, select random elements
        if selected_artistic_modifier is None:
            selected_artistic_modifier = random.choice(artistic_modifier)
        if selected_art_style is None:
            selected_art_style = random.choice(art_styles)
        if selected_art_modifier is None:
            selected_art_modifier = random.choice(art_modifiers)
        if selected_photorealistic_modifier is None:
            selected_photorealistic_modifier = random.choice(photorealistic_modifiers)
        if selected_lighting_modifier is None:
            selected_lighting_modifier = random.choice(lighting_modifiers)

        # Construct the final prompt by combining the user's subject and selected categories
        final_prompt = f"{user_subject} {selected_artistic_modifier} {selected_art_style} {selected_art_modifier} {selected_photorealistic_modifier} {selected_lighting_modifier}"

        # Send the final prompt to DALL·E 2 to generate an image
        response = openai.Image.create(prompt=final_prompt, n=1, size="1024x1024")

        # Get the generated image URL from the response
        image_url = response["data"][0]["url"]

        # Send the updated prompt along with the generated image URL
        await ctx.send(f"Updated Prompt: `{final_prompt}`")
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot with the provided token
bot.run(BOT_TOKEN)
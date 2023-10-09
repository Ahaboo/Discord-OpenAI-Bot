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

# Context that will be used to generate AI Art, Change context to anything that you want
art_context = "A user will give you a prompt that contains a subject and could contain different modifiers, if the user gives you a modifier that fits into these categories artistic_modifier = [ Salvador Dali , Norman Rockwell , Banksy (Street Art) , Tim Burton , Takashi Murakami , Van Gogh , Warhol \
    ]art_styles = [ Digital Art , Steampunk Art , Cyberpunk Art , ukiyo-e Art , Deco Art , Vector Art , Low Poly Art , Glitchcore Art , Bauhaus Art , Modern Art , Coloring Book , Line Art , Vapowrwave Art , Ball-point Pen Art , pencil sketch/pencil drawing \
        , anime , grafitti art , cartoon art , stock art , 3d art , watercolor art ]art_modifiers = [ detailed , Award-Winning Art , Trending on ArtStation , Photorealistic , Unreal Engine , Fanart ]photorealistic_modifiers = [ 4k/8k , 15mm wide-angle lens\
              , 35mm lens , 85 mm lens , 200 mm lens , Bokeh , Award-Winning , Tilt-Shift Photography , Cinematic Movie Photograph , Macro ]lighting_modifiers = [ Cinematic Lighting , At/During Golden Hour , Golden Hour Sunlight , Ambient Lighting , Studio \
                Lighting , Lens Flare ]Then take it out of his prompt and set that category to what the user selected, if the user misses any categories select one randomly out of the list for each category. Return a single setence. Must have one of each category no matter what ExampleInput: !generate\
                      a octopus running away from a dog Output: octopus running away from dog ,Van Gogh ,Digital Art ,detailed ,15mm wide-angle lens Cinematic Lighting"

# Create a Discord bot instance
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Define a data class to store session information
class Session:
    def __init__(self):
        self.context = []  # Initialize context as an empty list

# Initialize a session
session = Session()


# Bot Context, change context to fit your desired bot's personality
bot_context = [
    {"role": "system", "content": "Enter Your Bots Personality Here"}
]
# Event handler for when the bot is ready
@bot.event
async def on_ready():
    # Send a welcome message to the specified channel
    channel = bot.get_channel(int(CHANNEL_ID))
    await channel.send("Enter your welcome message here")

# Variable to track whether a command is in progress
command_in_progress = False

@bot.event
async def on_message(message):
    global command_in_progress  # Use the global variable

    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if message.content.startswith('!'):
        # If the message starts with a command prefix, execute the command
        await bot.process_commands(message)
        command_in_progress = True  # Set command_in_progress to True
        return  # Exit the event handler

    if command_in_progress:
        return  # Ignore messages when a command is in progress

    # If the message is not a command, combine it with the bot's context and respond as before
    combined_messages = bot_context + [{"role": "user", "content": message.content}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=combined_messages,
    )

    bot_response = response.choices[0].message["content"].strip()

    if "messages" in response.choices[0].message:
        session.context = response.choices[0].message["messages"]

    await message.channel.send(bot_response)

    # Reset command_in_progress to False after responding
    command_in_progress = False

# Generate Command
@bot.command()
async def generate(ctx, *, prompt=None):
    try:
        if prompt is None:
            await ctx.send("Please provide a prompt for AI image generation.")
            return

        if len(prompt) < 4:
            await ctx.send("Please provide a valid prompt with at least 4 characters.")
            return

        prompt_with_context = f"Context: {art_context}\nUser Prompt: {prompt}"

        # Send the user's prompt to ChatGPT-3 using the chat/completions endpoint
        new_prompt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the chat model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_with_context},
            ],
        )

        # Get the generated response from ChatGPT-3
        bot_response = new_prompt.choices[0].message["content"].strip()

        # Allow the user to edit the generated prompt
        await ctx.send("Generated Prompt: " + bot_response)
        await ctx.send("You can now edit the prompt. Type your edits or 'continue' to proceed.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            user_response = await bot.wait_for("message", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Prompt editing timed out. Using the generated prompt.")
        else:
            if user_response.content.lower() != "continue":
                # User provided edits
                bot_response = user_response.content

        # Send the updated prompt back to the user
        await ctx.send("Updated Prompt: " + bot_response)

        # Send the user's prompt to DALL·E 2 to generate an image
        response = openai.Image.create(prompt=bot_response, n=1, size="1024x1024")

        # Get the generated image URL from the response
        image_url = response["data"][0]["url"]

        # Send the generated image URL back to the user
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Music Command
@bot.command()
async def music(ctx, *, prompt=None):
    try:
        if prompt is None:
            await ctx.send("Please provide a prompt for the music command.")
            return

        if len(prompt) < 4:
            await ctx.send("Please provide a valid prompt with at least 4 characters.")
            return

        # Define the context for the music command
        music_context = "Context: You will receive input from a user talking about music or a type of music, you should then respond with a popular song based on their request, your output should only be a single sentence with the name of a song, and then 4-5 words that make a stern but funny comment about the user's choice, for example, input: A slow jazz song, example output: 'Fly Me to the Moon' - Well, you've got good taste!"

        prompt_with_context = f"Context: {music_context}\nUser Prompt: {prompt}"

        # Send the user's prompt to ChatGPT-3 using the chat/completions endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the chat model
            messages=[
                {"role": "system", "content": prompt_with_context},
            ],
        )

        # Get the generated response from ChatGPT-3
        bot_response = response.choices[0].message["content"].strip()

        # Send the song recommendation and funny comment back to the user
        await ctx.send(bot_response)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot with the provided token
bot.run(BOT_TOKEN)
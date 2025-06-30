import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} has connected")

@bot.command(name='apply')
async def apply(ctx):
    user = ctx.author

    # Safely attempt to delete the original command
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print("⚠️ Bot lacks permission to delete the message.")
    except discord.HTTPException as e:
        print(f"⚠️ Message deletion failed: {e}")

    # Check that messages come from the correct user and are DMs
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)

    try:
        await user.send("📝 Let's begin your Valorant lobby application!")

        await user.send("1️⃣ What's the name of your lobby?")
        lobby_name = await bot.wait_for("message", check=check, timeout=120)

        await user.send("🌍 What region are you playing in? (North America, Europe, Pacific, China)")
        region = await bot.wait_for("message", check=check, timeout=60)

        await user.send("🫂 What is the maximum number of players allowed in this lobby?")
        player_count = await bot.wait_for("message", check=check, timeout=60)

        await user.send("⌚ When is the lobby scheduled to start?")
        start_time = await bot.wait_for("message", check=check, timeout=90)

        await user.send("📝 Any additional notes or rules?")
        notes = await bot.wait_for("message", check=check, timeout=120)

        submission = (
            f"📬 **New Lobby Application Submitted by {user.mention}**\n\n"
            f"**Lobby Name:** {lobby_name.content}\n"
            f"**Region:** {region.content}\n"
            f"**Maximum Players:** {player_count.content}\n"
            f"**Scheduled Start Time:** {start_time.content}\n"
            f"**Additional Notes:** {notes.content}"
        )

        mod_channel_id = 1389054759171919892
        public_channel_id = 1389054777853345812
        mod_channel = bot.get_channel(mod_channel_id)

        if not mod_channel:
            await user.send("⚠️ Could not find the moderator channel. Please contact an admin.")
            return

        message = await mod_channel.send(submission)

        # Add approval/denial reactions
        try:
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        except discord.HTTPException as e:
            print(f"⚠️ Reaction error: {e}")
            await user.send("❌ Failed to add approval options. Please contact a moderator.")
            return

        await user.send("✅ Your lobby application has been submitted to the moderators.")

        def reaction_check(reaction, reactor):
            return (
                reaction.message.id == message.id and
                str(reaction.emoji) in ["✅", "❌"] and
                reactor.guild_permissions.manage_messages
            )

        try:
            reaction, reactor = await bot.wait_for("reaction_add", check=reaction_check, timeout=3600)

            if str(reaction.emoji) == "✅":
                public_channel = bot.get_channel(public_channel_id)
                if public_channel:
                    await public_channel.send(
                        f"✅ **Approved Lobby by {user.mention}**\n\n"
                        f"**Lobby Name:** {lobby_name.content}\n"
                        f"**Region:** {region.content}\n"
                        f"**Maximum Players:** {player_count.content}\n"
                        f"**Scheduled Start Time:** {start_time.content}\n"
                        f"**Additional Notes:** {notes.content}"
                    )
                    await user.send("✅ Your lobby has been approved and posted!")
            elif str(reaction.emoji) == "❌":
                await user.send("❌ Your lobby application was denied by a moderator.")
        except asyncio.TimeoutError:
            await user.send("⌛ The approval process timed out. Please try again later.")

    except asyncio.TimeoutError:
        await user.send("⌛ Timeout reached. Please restart the application process with `?apply`.")
    except discord.Forbidden:
        print("⚠️ Couldn't send a DM. User may have DMs closed.")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    try:
        await user.send(f"⚠️ Error: {type(e).__name__}: {e}")
    except discord.Forbidden:
        print("⚠️ Could not DM the user. They might have DMs turned off.")

bot.run(TOKEN)

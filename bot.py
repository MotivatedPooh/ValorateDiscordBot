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

    try:
        await user.send("📝 Let's begin your Valorant lobby application!")

        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)

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
        try:
            mod_channel = await bot.fetch_channel(mod_channel_id)
            print("Fetched mod_channel:", mod_channel)
        except Exception as e:
            print(f"Failed to fetch mod channel: {e}")
            mod_channel = None

        if mod_channel:
            message = await mod_channel.send(submission)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def reaction_check(reaction, reactor):
                return (
                    reaction.message.id == message.id and
                    str(reaction.emoji) in ["✅", "❌"] and
                    reactor.guild_permissions.manage_messages
                )

            try:
                reaction, reactor = await bot.wait_for("reaction_add", check=reaction_check, timeout=3600)

                if str(reaction.emoji) == "✅":
                    public_channel_id = 1389106877371252816
                    public_channel = await bot.fetch_channel(public_channel_id)
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
                print("⌛ No moderator reacted in time.")
                await user.send("⌛ No response from moderators. Please check back later.")
        else:
            await user.send("⚠️ Could not find the moderator channel. Please contact an admin.")

    except discord.Forbidden:
        print("❌ Could not DM the user. They might have DMs off.")
    except asyncio.TimeoutError:
        try:
            await user.send("⌛ You took too long to respond. Please restart with `?apply`.")
        except discord.Forbidden:
            print("❌ Timeout notice could not be sent. DMs are blocked.")

bot.run(TOKEN)

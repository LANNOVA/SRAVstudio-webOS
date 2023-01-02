import discord
from discord.ext import commands

# discord_slash is the library I use for Button components
from discord_slash import SlashCommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    ComponentContext,
    create_actionrow,
    create_button,
)

client = commands.Bot(command_prefix="-", case_insensitive=True, help_command=None)
# yes it says slash, but slash commands are not used and this is required for buttons.
slash = SlashCommand(client)

# Remember to edit these!
TICKET_MOD_ROLE_ID = 1234567890
MANAGEMENT_ROLE_ID = 1234567890
GUILD_ID = 1234567890

TICKET_CATEGORY_NAME = "Active Tickets"

# Ignore these
ticket_category = None
ticket_mod_role = None
management_role = None
guild = None


@client.event
async def on_ready():
    print("Bot is ready")

    global guild, ticket_category, ticket_mod_role, management_role  # one of the annoying things about Python...

    # get the guild
    guild = client.get_guild(GUILD_ID)

    # replace Active Tickets the exact name of your category (case sensitive)
    ticket_category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)

    ticket_mod_role = guild.get_role(
        role_id=TICKET_MOD_ROLE_ID
    )  # ticket moderator role
    management_role = guild.get_role(role_id=MANAGEMENT_ROLE_ID)  # management role


# called whenever a button is pressed
@client.event
async def on_component(ctx: ComponentContext):
    await ctx.defer(
        ignore=True
    )  # ignore, i.e. don't do anything *with the button* when it's pressed.

    ticket_created_embed = discord.Embed(
        title="Ticket Processed",
        description=f"""Hey {ctx.author.name}! Thanks for opening a ticket with us today, but before we transfer you through to a manager, we have to approve your ticket. We have this step in place to prevent bots and spam tickets.
        Please describe your enquiry and our team will approve it shortly. We thank you in advance for your patience.""",
    )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True),
        guild.me: discord.PermissionOverwrite(view_channel=True),
        ticket_mod_role: discord.PermissionOverwrite(view_channel=True),
    }

    ticket = await ticket_category.create_text_channel(
        f"{ctx.author.name}-{ctx.author.discriminator}", overwrites=overwrites
    )

    await ticket.send(
        ctx.author.mention, embed=ticket_created_embed
    )  # ping the user who pressed the button, and send the embed


@client.command()
@commands.has_role(TICKET_MOD_ROLE_ID)
async def sendticket(ctx):
    embed = discord.Embed(
        title="Contact Support",
        description="Click the button below to open a ticket",
    )

    actionrow = create_actionrow(
        *[
            create_button(
                label="Open Ticket", custom_id="ticket", style=ButtonStyle.primary
            ),
        ]
    )

    await ctx.send(embed=embed, components=[actionrow])


@client.command(aliases=["approve"])
@commands.has_role(TICKET_MOD_ROLE_ID)
async def up(ctx):
    overwrites = {
        ctx.guild.me: discord.PermissionOverwrite(view_channel=True),
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ticket_mod_role: discord.PermissionOverwrite(view_channel=None),
        management_role: discord.PermissionOverwrite(view_channel=True),
    }
    await ctx.channel.edit(overwrites=overwrites)

    await ctx.channel.send(
        "Ticket Approved!\nYour ticket has been approved and has been transferred through to the Management Team. They will assist you further with your enquiry."
    )


@client.command()
@commands.has_role(TICKET_MOD_ROLE_ID)
async def close(ctx):
    try:
        if int(ctx.channel.name[-4:]) > 0:
            await ctx.channel.delete()
        else:
            await ctx.send("❌ This does not seem like a ticket channel.")
    except:
        await ctx.send("❌ This does not seem like a ticket channel.")




client.run('MTA0OTI1NDQwMTQzMDI3ODIxNg.Gy4PnR.1zNOeDnMw5ZWVlvx5-bXxYe35OcHA2KIAIKlh0')
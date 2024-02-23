# Giveaway Management Bot
# Made by @xeltexynos
# Version: 3.0.0

print("Importing Libraries...")
import pyrogram
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import filters

import random
import database

import os
from datetime import datetime
import asyncio
import varfile

print("Starting Client...")
app = pyrogram.Client(
    name="giveaway",
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    bot_token=varfile.bot_token,
    in_memory=True,
)

print("Initializing Configuration...")
if varfile.test_mode:
    print("Test Mode Activated!")
    channel_id = varfile.test_channel_id
    group_id = varfile.test_group_id

print("Initializing Database...")
root = database.create_db()


def preliminaries():
    pass


def printlog(message, end=""):
    if end != "":
        print(message, end=end)
    else:
        print(message)

    if not varfile.test_mode:
        current_time = datetime.now().strftime(format="%H:%M:%S")
        current_date = datetime.now().strftime(format="%Y-%m-%d")
        if not os.path.exists(path="logs"):
            os.makedirs(name="logs")
        with open(
            file=(os.path.join("logs", f"{current_date}.log")),
            mode="a+",
            encoding="utf-8",
        ) as log:
            log.write(f"[{current_time}] {message}\n")


@app.on_message(
    filters=filters.user(users=varfile.admins)
    & filters.private
    & ~filters.command(
        commands=[
            "abort",
            "stats",
            "start",
            "settime",
            "ban",
            "unused",
            "unban",
            "cleardata",
        ]
    )
)
async def poster(_, message: Message):
    printlog(message=f"Message received from {message.from_user.id}!")
    if message.caption:
        printlog(message=f"Sending Post to channel...")
        message_sent = await app.send_photo(
            chat_id=channel_id,
            caption=message.caption.markdown,
            photo=message.photo.file_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Register!",
                            url=f"https://t.me/{varfile.bot_username}?start=register",
                        )
                    ]
                ]
            ),
        )

        printlog(message=f"Executing DB Commands...")
        database.set_post_id(post_id=message_sent.id)
        database.clear_users()

        printlog(message=f"Post sent to channel!")
        await message.reply(text="Sent!")

    else:
        if root["post_id"] == None:
            return

        if root["time"]["total"] == 0:
            await message.reply(text="Time not set!")

        printlog(message=f"Collecting Codes...")
        await message.reply(
            text=f"Starting the giveaway in {root['time']['total']/3600} hours, To abort, send /abort"
        )

        printlog(message="Configuring Variables...")
        codes = message.text.split(sep="\n")
        database.clear_chosen()
        database.add_codes(codes=codes)

        printlog(message="Starting Timer...")
        zfill_num = len(str(object=root["time"]["total"]))

        for i in range(round(number=root["time"]["total"])):
            print(
                "Time left: " + str(object=root["time"]["total"] - i).zfill(zfill_num),
                end="\r",
            )

            if (root["time"]["total"] - i) % 60 == 0:
                root["time"]["left"] = root["time"]["total"] - i
                database.save_db(data=root)

            await asyncio.sleep(delay=1)

        printlog(message="\nEnding Giveaway...")
        try:
            await app.edit_message_reply_markup(
                chat_id=channel_id, message_id=root["post_id"], reply_markup=None
            )
        except:
            pass

        printlog(message="Choosing Winners...")
        for _ in range(len(codes)):
            while True:
                try:
                    user = await app.get_users(
                        user_ids=random.choice(seq=list(root["users"]))
                    )
                except Exception as e:
                    print(e)
                    continue
                break

            database.mark_chosen(user_id=user.id)

        printlog(message="Sending Messages...")
        for i in range(len(codes)):
            user = await app.get_users(user_ids=root["chosen"][i])

            await app.send_message(
                chat_id=group_id,
                text=f"{user.mention()}:[{root['chosen'][i]}](tg://user?id={root['chosen'][i]}) click on the button below to receive your present! You have 6 hours to do so :D",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Redeem!",
                                url=f"https://t.me/{varfile.bot_username}?start=redeem",
                            )
                        ]
                    ]
                ),
            )

            await asyncio.sleep(delay=30)

        database.clear_post_id()

        printlog(message="Sending Winner List...")
        users = await app.get_users(user_ids=root["chosen"])
        msg = await app.send_message(
            chat_id=group_id,
            text="Giveaway has ended! List of winners: \n"
            + "\n".join([f"{x.mention()}:{x.id}" for x in users])
            + "\n\nBot by @XelteXynos",
        )
        await app.pin_chat_message(chat_id=group_id, message_id=msg.id)

        printlog(message="Starting Timer...\n")
        for i in range(21600):
            print(
                "Time left: " + str(object=21600 - i).zfill(zfill_num),
                end="\r",
            )
            await asyncio.sleep(delay=1)

        printlog(message="\nCollecting Unused Codes...")
        await message.reply(
            text="Unused Codes:\n\n"
            + "\n".join([x for x in root["codes"] if x not in root["used_codes"]])
        )

        quit()


@app.on_message(
    filters=filters.command(commands="start", prefixes="/") & filters.private
)
async def start(_, message: Message):
    if len(message.command) == 1:
        return

    if message.command[1] == "register":
        if (
            root["post_id"] == None
            or message.from_user.id in root["chosen"]
            or message.from_user.id in root["banned"]
            or message.from_user.id in root["users"]
        ):
            return

        printlog(message=f"Registering {message.from_user.id}...")

        if message.from_user.id not in root["users"]:
            database.add_user(user_id=message.from_user.id)

            if len(root["users"]) % 10 == 0:
                await app.send_message(
                    chat_id=group_id,
                    text=f'{len(root["users"])}+ users have registered!',
                )

            printlog(message=f"User {str(object=message.from_user.id)} has registered!")

            await message.reply(text="You're registered!")

        return

    elif message.command[1] == "redeem":
        if message.from_user.id not in root["chosen"]:
            return

        code = root["codes"][root["chosen"].index(message.from_user.id)]

        if code not in root["used_codes"]:
            await message.reply(
                text="You've won the giveaway! Here's your redeem code: " + code
            )

            database.mark_used(code=code, user_id=message.from_user.id)

            try:
                printlog(message=f"{code} has been redeemed by {message.from_user.first_name}")
            except:
                printlog(message=f"{code} has been redeemed by {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="cleardata", prefixes="/")
    & filters.private
    & filters.user(users=varfile.admins)
)
async def cleardata(_, message: Message):
    printlog(message=f"Clearing data on command of {message.from_user.id}...")
    database.clear_db()
    await message.reply(text="Data cleared!")
    printlog(message=f"Data cleared on command of {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="unused", prefixes="/")
    & filters.private
    & filters.user(users=varfile.admins)
)
async def unused(_, message: Message):
    printlog(message=f"Sending unused codes to {message.from_user.id}...")
    unused_codes = [x for x in root["codes"] if x not in root["used_codes"]]

    if len(unused_codes) == 0:
        await message.reply(text="No unused codes!")
        return

    await message.reply(text="Unused Codes:\n\n" + "\n".join(unused_codes))

    printlog(message=f"Unused codes sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="abort", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def abort(_, message: Message):
    await message.reply(text="Aborted!")
    printlog(message=f"Bot has been aborted on command of {message.from_user.id}")
    quit()


@app.on_message(
    filters=filters.command(commands="stats", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def stats(_, message: Message):
    printlog(message=f"Sending stats to {message.from_user.id}...")

    await message.reply(
        text=f"Time: {root['time']['left']}/{root['time']['total']}\n\nUsers: {len(root['users'])}\n\nCodes: {len(root['codes'])}\n\nChosen: {len(root['chosen'])}\n\nBanned: {len(root['banned'])}\n\nUsed Codes: {len(root['used_codes'])}\n\nPost ID: {root['post_id']}"
    )

    printlog(message=f"Stats sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="settime", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def settime(_, message: Message):
    try:
        printlog(f"Setting time to {message.text.split(' ')[1]} hours...")

        root["time"]["total"] = round(float(message.command[1]) * 3600)
        database.save_db(data=root)

        printlog(f"Time set to {root['time']['total']/3600} hours!")

        await message.reply("Time set!")
    except:
        await message.reply("Invalid Time!")


@app.on_message(
    filters=filters.command(commands="ban", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def ban(_, message: Message):
    printlog(f"Banning user on command of {message.from_user.id}...")
    try:
        user_id = await app.get_users(user_ids=message.command[1])
        user_id = user_id.id
    except:
        await message.reply("Invalid User!")
        return

    if user_id in root["banned"]:
        await message.reply("User is already banned!")
        return

    if user_id in root["users"]:
        root["users"].remove(user_id)

    database.ban_user(user_id=user_id)

    printlog(f"User {str(object=user_id)} has been banned!")

    await message.reply("Banned!")


@app.on_message(
    filters=filters.command(commands="unban", prefixes="/")
    & filters.user(users=varfile.admins)
    & filters.private
)
async def unban(_, message: Message):
    printlog(f"Unbanning user on command of {message.from_user.id}...")
    try:
        user_id = await app.get_users(user_ids=message.command[1])
        user_id = user_id.id
    except:
        await message.reply("Invalid User!")
        return

    if user_id not in root["banned"]:
        await message.reply("User is not present in banned list!")
        return

    database.unban_user(user_id=user_id)

    printlog(f"User {str(object=user_id)} has been unbanned!")

    await message.reply("Unbanned!")


preliminaries()
print("Started...")
app.run()

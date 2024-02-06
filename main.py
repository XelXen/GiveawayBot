# Giveaway Management Bot
# Made by @xeltexynos
# Version: 2.6.0

print("Importing Libraries...")
import pyrogram
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import filters
import random
import ZODB
import ZODB.FileStorage
import os
from datetime import datetime
import transaction
import asyncio
from varfile import *

print("Starting Client...")
app = pyrogram.Client(
    name="giveaway",
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    bot_token=bot_token,
    in_memory=True,
)

print("Initializing Configuration...")
if test_mode:
    channel_id = test_channel_id
    group_id = test_group_id

storage = ZODB.FileStorage.FileStorage(database)
db = ZODB.DB(storage)
conn = db.open()
root = conn.root()

if not "codes" in root:
    root["codes"] = []
if not "chosen" in root:
    root["chosen"] = []
if not "time" in root:
    root["time"] = {"total": 0, "left": 0}
if not "post_id" in root:
    root["post_id"] = None
if not "users" in root:
    root["users"] = set()
if not "used_codes" in root:
    root["used_codes"] = []
if not "banned" in root:
    root["banned"] = set()

transaction.commit()


def printlog(message, end=""):
    if end != "":
        print(message, end=end)
    else:
        print(message)
    
    if not test_mode:
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists("logs"):
            os.makedirs("logs")
        with open((os.path.join("logs", f"{current_date}.log")), "a+", encoding="utf-8") as log:
            log.write(f"[{current_time}] {message}\n")

@app.on_message(
    filters=filters.user(users=admins)
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
            "cleardata"
        ]
    )
)
async def poster(_, message: Message):
    printlog(f"Message received from {message.from_user.id}!")
    if message.caption:
        printlog(f"Sending Post to channel...")
        message_sent = await app.send_photo(
            chat_id=channel_id,
            caption=message.caption.markdown,
            photo=message.photo.file_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Register!", url=f"https://t.me/{bot_username}?start=register"
                        )
                    ]
                ]
            ),
        )

        printlog(f"Configuring Variables...")
        root["post_id"] = message_sent.id
        root["users"] = set()
        transaction.commit()

        printlog(f"Post sent to channel!")
        await message.reply("Sent!")

    else:
        if root["post_id"] == None:
            return
        
        if root["time"]["total"] == 0:
            await message.reply("Time not set!")

        printlog(f"Collecting Codes...")
        await message.reply(
            f"Starting the giveaway in {root['time']['total']/3600} hours, To abort, send /abort"
        )

        printlog("Configuring Variables...")
        codes = message.text.split("\n")
        root["chosen"] = []
        root["codes"] = codes
        transaction.commit()

        printlog("Starting Timer...")
        zfill_num = len(str(object=root["time"]["total"]))

        for i in range(round(root["time"]["total"])):
            print(
                "Time left: " + str(object=root["time"]["total"] - i).zfill(zfill_num),
                end="\r",
            )

            if (root["time"]["total"] - i) % 60 == 0:
                root["time"]["left"] = root["time"]["total"] - i
                transaction.commit()

            await asyncio.sleep(delay=1)

        print("\nEnding Giveaway...")
        try:
            await app.edit_message_reply_markup(
                chat_id=channel_id, message_id=root["post_id"], reply_markup=None
            )
        except:
            pass

        printlog("Choosing Winners...")
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

            root["chosen"].append(user.id)
            root["users"].remove(user.id)

        transaction.commit()

        printlog("Sending Messages...")
        for i in range(len(codes)):
            user = await app.get_users(user_ids=root["chosen"][i])

            await app.send_message(
                chat_id=group_id,
                text=f"{user.mention()}:[{root['chosen'][i]}](tg://user?id={root['chosen'][i]}) click on the button below to receive your present! You have 6 hours to do so :D",
                reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Redeem!", url=f"https://t.me/{bot_username}?start=redeem"
                        )
                    ]
                ]
            ),
            )

            await asyncio.sleep(delay=30)

        root["post_id"] = None
        transaction.commit()

        printlog("Sending Winner List...")
        users = await app.get_users(user_ids=root["chosen"])
        msg = await app.send_message(
            chat_id=group_id,
            text="Giveaway has ended! List of winners: \n"
            + "\n".join([f"{x.mention()}:{x.id}" for x in users])
            + "\n\nBot by @XelteXynos",
        )
        await app.pin_chat_message(chat_id=group_id, message_id=msg.id)

        printlog("Starting Timer...\n")
        for i in range(21600):
            print(
                "Time left: " + str(21600 - i).zfill(zfill_num),
                end="\r",
            )
            await asyncio.sleep(delay=1)

        print("\nCollecting Unused Codes...")
        await message.reply(
            "Unused Codes:\n\n"
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
        if root["post_id"] == None or message.from_user.id in root["chosen"] or message.from_user.id in root["banned"]:
            return

        printlog(f"Registering {message.from_user.id}...")
        
        if message.from_user.id not in root["users"]:
            root["users"].add(message.from_user.id)
            transaction.commit()

            if len(root["users"]) % 10 == 0:
                await app.send_message(
                    chat_id=group_id, text=f'{len(root["users"])}+ users have registered!'
                )

            printlog(f"User {str(object=message.from_user.id)} has registered!")

            await message.reply("You're registered!")

        return

    elif message.command[1] == "redeem":
        if message.from_user.id not in root["chosen"]:
            return

        code = root["codes"][root["chosen"].index(message.from_user.id)]

        if code not in root["used_codes"]:
            await message.reply("You've won the giveaway! Here's your redeem code: " + code)
            
            root["used_codes"].append(code)
            transaction.commit()
            
            try:
                printlog(f"{code} has been redeemed by {message.from_user.first_name}")
            except:
                printlog(f"{code} has been redeemed by {message.from_user.id}")


@app.on_message(filters=filters.command(commands="cleardata", prefixes="/") & filters.private & filters.user(users=admins))
async def cleardata(_, message: Message):
    printlog(f"Clearing data on command of {message.from_user.id}...")
    root["codes"] = []
    root["chosen"] = []
    root["time"] = {"total": 0, "left": 0}
    root["post_id"] = None
    root["users"] = set()
    root["used_codes"] = []
    root["banned"] = set()
    transaction.commit()

    await message.reply("Data cleared!")
    printlog(f"Data cleared on command of {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="unused", prefixes="/")
    & filters.private
    & filters.user(users=admins)
)
async def unused(_, message: Message):
    printlog(f"Sending unused codes to {message.from_user.id}...")
    unused_codes = [x for x in root["codes"] if x not in root["used_codes"]]

    if len(unused_codes) == 0:
        await message.reply("No unused codes!")
        return

    await message.reply(
        "Unused Codes:\n\n"
        + "\n".join(unused_codes)
    )

    printlog(f"Unused codes sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="abort", prefixes="/")
    & filters.user(users=admins)
    & filters.private
)
async def abort(_, message: Message):
    await message.reply("Aborted!")
    printlog(f"Bot has been aborted on command of {message.from_user.id}")
    try:
        transaction.commit()
    except:
        pass
    db.close()
    quit()


@app.on_message(
    filters=filters.command(commands="stats", prefixes="/")
    & filters.user(users=admins)
    & filters.private
)
async def stats(_, message: Message):
    printlog(f"Sending stats to {message.from_user.id}...")
    
    await message.reply(
        f"Time: {root['time']['left']}/{root['time']['total']}\n\nUsers: {len(root['users'])}\n\nCodes: {len(root['codes'])}\n\nChosen: {len(root['chosen'])}\n\nBanned: {len(root['banned'])}\n\nUsed Codes: {len(root['used_codes'])}\n\nPost ID: {root['post_id']}"
    )

    printlog(f"Stats sent to {message.from_user.id}")


@app.on_message(
    filters=filters.command(commands="settime", prefixes="/")
    & filters.user(users=admins)
    & filters.private
)
async def settime(_, message: Message):
    try:
        printlog(f"Setting time to {message.text.split(' ')[1]} hours...")
        
        root["time"]["total"] = round(float(message.command[1]) * 3600)
        transaction.commit()

        printlog(f"Time set to {root['time']['total']/3600} hours!")

        await message.reply("Time set!")
    except:
        await message.reply("Invalid Time!")


@app.on_message(
    filters=filters.command(commands="ban", prefixes="/")
    & filters.user(users=admins)
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

    root["banned"].add(user_id)
    transaction.commit()

    printlog(f"User {str(object=user_id)} has been banned!")

    await message.reply("Banned!")


@app.on_message(
    filters=filters.command(commands="unban", prefixes="/")
    & filters.user(users=admins)
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

    root["banned"].remove(user_id)
    transaction.commit()

    printlog(f"User {str(object=user_id)} has been unbanned!")

    await message.reply("Unbanned!")


printlog("Started...")
app.run()

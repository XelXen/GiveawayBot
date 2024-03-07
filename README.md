# GiveawayBot

Manage giveaways on Telegram using a simple pyrogram script :D

## Features

1. **Easy Registration**: The bot can manage and handle the registrations using a simple inline button.
2. **Time Limit**: Each giveaway can have a custom time limit.
3. **Redeem Feature**: Winners can redeem their prizes in their DM.
4. **Winner Selection**: The bot randomly selects winners from the participants.
5. **Winner Announcements**: The bot sends a message to the group announcing the winners.
6. **Logging**: The bot logs important events like the start of the timer and the sending of the winner list.
7. **Prelim Execution**: Execute a few database commands before starting the main script
8. **Testing Mode**: Use the bot in a testing environment (a seperate test channel and group) to avoid spamming the main group
9. **On-Demand Abort**: Abort the giveaway at any time
10. **Unused Codes**: Get a list of unused codes
11. **Blacklisting**: Blacklist users from participating in the giveaway

## Prerequisites

- `pyrogram`
- `tgcrypto` (optional but recommened for faster perf.)

## Installation

1. Download the [latest release zip](https://github.com/XelXen/GiveawayBot/releases/latest) and extract it to a folder
2. Open the repository folder in the terminal
3. Install the requirements: `pip install -r requirements.txt`
4. Rename `varfile.rename` to `varfile.py`

## Usage

1. Configure varfile.py
2. Run the script: `python main.py`
3. Add the bot to the groupchat of the channel and the channel and give it messaging permissions
4. Use `/settime 6` to set giveaway time to 6 hours but you can configure it with any number you want
5. Send the bot a giveaway post
6. Send the bot giveaways codes (one code per line)

## Commands

- `/unused`: Get a list of unused codes
- `/settime <time>`: Set the time limit for the giveaway
- `/ban <user_id>`: Ban a user from participating in the giveaway
- `/unban <user_id>`: Unban a user from participating in the giveaway
- `/abort`: Abort the giveaway
- `/stats`: Get the stats from Database

## License

This project is licensed under the Mozilla Public License Version 2.0 - see the [LICENSE](LICENSE) file for details.

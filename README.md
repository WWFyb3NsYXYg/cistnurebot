
<h3 align="right"> <a href="README-UA.md"> <img src="https://user-images.githubusercontent.com/87089735/213570989-5be18f9b-fb96-48ae-bb10-ed0b02ac971b.png" height="20px"> Українська </a></h3>

# CIST Telegram Bot

This is a Telegram bot that provides information about the schedule of a specific group in the Kharkiv National University of Radio Electronics (NURE). The bot uses the CIST API to retrieve the schedule information.


<p align="center">
  
<img src="https://github.com/WWFyb3NsYXYg/cistnurebot/assets/87089735/70942ce0-4c8a-4923-8f4e-86f6b2eab759" height="400px">
<p>
  
## Getting Started

To use this bot, you need to follow these steps:

1. Create a new bot using the [BotFather](https://telegram.me/BotFather) and obtain the bot token.
2. Enable inline mode for the bot by sending the `/setinline` command to the BotFather.
3. Clone this repository to your local machine.
4. Install the required dependencies by running `pip install -r requirements.txt`.
5. Run the `gen_file.py` script to generate the `config.py` file in the root directory of the project. Make sure to enter the Telegram bot token and NURE group name as prompted in the console. Do not modify the format of the input.
6. Run the `bot.py` script to start the bot.

## Usage

Once the bot is running, you can interact with it by sending commands in a Telegram chat. Here are the available commands:

- **Manual Update Command**: Authorized users can manually update and send the current schedule to the designated channel using the `/update` command.
- **Scheduled Updates**: Daily schedule updates are sent to a specified Telegram channel at 7:30 AM.
- **Date-Specific Schedule**: Users can request the schedule for a specific date using the `/schedule [DD.MM]`. You can use it with a date argument in the DD.MM format. If the argument is missing, the current day is used.
- In inline mode, you can use the bot's tag (@YourBotUsername) to select the schedule. For example, `@YourBotUsername` will show today's schedule, and `@YourBotUsername 13.11` will show the schedule for November 13th.

## Contributing

If you want to contribute to this project, feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.




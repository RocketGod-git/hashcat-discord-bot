# Hashcat Discord Bot

Harness the power of Hashcat directly from Discord. Crack hashes with ease and efficiency using the renowned Hashcat password recovery tool, all within the convenience of your Discord server.

```
 __________                  __             __     ________             .___ 
 \______   \  ____    ____  |  | __  ____ _/  |_  /  _____/   ____    __| _/ 
  |       _/ /  _ \ _/ ___\ |  |/ /_/ __ \\   __\/   \  ___  /  _ \  / __ |  
  |    |   \(  <_> )\  \___ |    < \  ___/ |  |  \    \_\  \(  <_> )/ /_/ |  
  |____|_  / \____/  \___  >|__|_ \ \___  >|__|   \______  / \____/ \____ |  
         \/              \/      \/     \/               \/              \/  
```

Created by [RocketGod](https://github.com/RocketGod-git)

## Setup & Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/RocketGod-git/hashcat-discord-bot.git
    ```

2. **Move to Hashcat Directory**

    Ensure you place the `./discordbot` folder from this repo into your main Hashcat directory.

3. **Install Required Libraries**

    ```bash
    pip install discord requests psutil
    ```

4. **Setup the Configuration**

    Edit the `config.json` file:
    - Replace `YOUR-BOT-TOKEN` with your Discord bot token.
    - Replace `FROM-DISCORD-DEVELOPER` with your Discord application ID.
    - Replace `YOUR-DISCORD-SERVER-ID` with your server's ID.

5. **Run the Bot**

    ```bash
    python hashcat.py
    ```

## Commands

- `/hashcat` - Use Hashcat to crack hashes. The command comes with various options such as:
  - Hash value
  - Hash type (e.g., MD5, SHA-1, etc.)
  - Attack mode (Dictionary or Bruteforce)
  - Wordlist (for dictionary attacks)
  - Password length (for bruteforce attacks)

## Wordlists

For dictionary attacks, you can utilize various wordlists. The bot is configured with the following options:

- **RockYou 2021** - [Download here](#)
- **RockYou Strong** - [Download here](#)
- **Crackstation** - [Download here](#)

Make sure to download and place these wordlists in main hashcat folder.

## Contributing

If you'd like to contribute or have suggestions for additional features, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the [AGPL-3.0 license](LICENSE) file for more details.

## Disclaimer

Please only use this bot responsibly and ethically. Unauthorized password cracking is illegal and unethical. Always have proper permissions before attempting to crack any hashes.

## Credits

- [RocketGod](https://github.com/RocketGod-git) for creating the bot.
- [Hashcat](https://hashcat.net/hashcat/) for the powerful password recovery tool.
- The creators of the provided wordlists.

![rocketgod_logo](https://github.com/RocketGod-git/shodanbot/assets/57732082/7929b554-0fba-4c2b-b22d-6772d23c4a18)
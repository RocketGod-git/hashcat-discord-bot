import requests
import json

def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def register_command():
    config = load_config()

    APPLICATION_ID = config.get("application_id")
    GUILD_ID = config.get("guild_id")
    BOT_TOKEN = config.get("discord_bot_token")

    # Endpoint URL for registering a guild-specific command
    url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"

    # JSON structure for the hashcat command
    command_data = {
        "name": "hashcat",
        "type": 1,
        "description": "Crack hashes using Hashcat",
        "options": [
            {
                "name": "hash",
                "description": "The hash value to be cracked",
                "type": 3,
                "required": True
            },
            {
                "name": "hashtype",
                "description": "The type of hash",
                "type": 3,
                "required": True,
                "choices": [
                    {"name": "MD5", "value": "md5"},
                    {"name": "SHA-1", "value": "sha1"},
                    {"name": "SHA-256", "value": "sha256"},
                    {"name": "SHA-512", "value": "sha512"},
                    {"name": "Samsung Android Password/PIN", "value": "samsungandroid"},
                    {"name": "Windows Hello PIN/Password", "value": "windowshello"},
                    {"name": "macOS", "value": "macos"},
                    {"name": "BitLocker", "value": "bitlocker"},
                    {"name": "Android FDE", "value": "androidfde"},
                    {"name": "APFS", "value": "apfs"},
                    {"name": "PDF", "value": "pdf"},
                    {"name": "MS Office", "value": "msoffice"},
                    {"name": "7-Zip", "value": "7zip"},
                    {"name": "RAR", "value": "rar"},
                    {"name": "WinZip", "value": "winzip"},
                    {"name": "iTunes backup", "value": "itunes"},
                    {"name": "Telegram", "value": "telegram"},
                    {"name": "Skype", "value": "skype"},
                    {"name": "Bitcoin", "value": "bitcoin"},
                    {"name": "Ethereum", "value": "ethereum"}
                ]
            },
            {
                "name": "attack_mode",
                "description": "Attack mode for hashcat",
                "type": 3,
                "required": True,
                "choices": [
                    {"name": "Dictionary", "value": "dictionary"},
                    {"name": "Bruteforce", "value": "bruteforce"}
                ]
            },
            {
                "name": "wordlist",
                "description": "Wordlist for dictionary attack",
                "type": 3,
                "required": False,
                "choices": [
                    {"name": "RockYou 2021", "value": "rockyou2021.txt"},
                    {"name": "RockYou Strong", "value": "rockyou_strong.txt"},
                    {"name": "Crackstation", "value": "crackstation.txt"}
                ]
            },
            {
                "name": "password_length",
                "description": "Password length for bruteforce attack (auto-fills mask with ?a)",
                "type": 4,  
                "required": False,
                "choices": [
                    {"name": "4", "value": 4},
                    {"name": "5", "value": 5},
                    {"name": "6", "value": 6},
                    {"name": "7", "value": 7},
                    {"name": "8", "value": 8},
                    {"name": "9", "value": 9},
                    {"name": "10", "value": 10},
                    {"name": "11", "value": 11},
                    {"name": "12", "value": 12},
                    {"name": "13", "value": 13},
                    {"name": "14", "value": 14},
                    {"name": "15", "value": 15},
                    {"name": "16", "value": 16}
                ]
            }
        ]
    }

    # Authorization header with your bot token
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}"
    }

    # Make the POST request to register the command
    response = requests.post(url, headers=headers, json=command_data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Command registered successfully!")
        print(response.json())  # Print the returned JSON data
    else:
        print(f"Failed to register command. Status code: {response.status_code}")
        print(response.text)  # Print the error message

if __name__ == "__main__":
    register_command()

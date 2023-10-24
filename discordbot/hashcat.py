# __________                  __             __     ________             .___ 
# \______   \  ____    ____  |  | __  ____ _/  |_  /  _____/   ____    __| _/ 
#  |       _/ /  _ \ _/ ___\ |  |/ /_/ __ \\   __\/   \  ___  /  _ \  / __ |  
#  |    |   \(  <_> )\  \___ |    < \  ___/ |  |  \    \_\  \(  <_> )/ /_/ |  
#  |____|_  / \____/  \___  >|__|_ \ \___  >|__|   \______  / \____/ \____ |  
#         \/              \/      \/     \/               \/              \/  
#
# Discord bot for Hashcat password cracking by RocketGod
# https://github.com/RocketGod-git/hashcat-discord-bot

import json
import logging
import discord
import os
import asyncio
import re
import sys
import psutil 
import requests

import register_command
from register_command import load_config

logging.basicConfig(level=logging.DEBUG)

if sys.platform == "win32":
    hashcat_exec = os.path.abspath("..\hashcat.exe")
else:
    hashcat_exec = os.path.abspath("../hashcat")

print(f"Executing hashcat at: {hashcat_exec}")

async def execute_hashcat(interaction, args, output_file, hash_type_mapping, hashtype, hash_value):
    try:
        # Check for existing hashcat processes
        for process in psutil.process_iter():
            try:
                pinfo = process.as_dict(attrs=['pid', 'name'])
                if "hashcat" in pinfo['name']:
                    await interaction.channel.send(f"Hashcat is currently cracking `{hash_value}` for {interaction.user.name}. Please wait and try again later.")
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Save the current working directory
        original_cwd = os.getcwd()
        hashcat_dir = os.path.dirname(hashcat_exec)
        os.chdir(hashcat_dir)
        
        args.extend(["-o", output_file])
        logging.info(f"Executing Hashcat with command: {' '.join(args)}")

        start_time = asyncio.get_running_loop().time()

        process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        while True:
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minutes
                # If we reach here, the process has finished, so you can log the results
                logging.info(f"Hashcat stdout: {stdout.decode()}")
                logging.info(f"Hashcat stderr: {stderr.decode()}")
                break  # Break out of the loop
            except asyncio.TimeoutError:
                # The process hasn't finished in 5 minutes, so send a message
                await interaction.channel.send(f"Still working on cracking `{hash_value}` for {interaction.user.name}.")
                
            # Check if 2 hours have passed
            if (asyncio.get_running_loop().time() - start_time) > 7200:  # 7200 seconds = 2 hours
                process.terminate()
                await interaction.channel.send("Hashcat took too long to respond. The process was terminated.")
                return

        if "All hashes found as potfile and/or empty entries! Use --show to display them." in stdout.decode():
            show_args = [hashcat_exec, "-m", hash_type_mapping[hashtype], hash_value, "--show"]
            process = await asyncio.create_subprocess_exec(*show_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                cracked_password = stdout.decode().split(":")[-1].strip()
                await interaction.channel.send(content=f"The hash `{hash_value}` has already been cracked: `{cracked_password}`")
            else:
                logging.error(f"Error when trying to show cracked password: {stderr.decode()}")
                await handle_errors(interaction, f"Hashcat encountered an error. Please contact a Mod for help.")
            return

        if process.returncode != 0:
            logging.error(f"Hashcat detailed error: {stderr.decode()}")
            await handle_errors(interaction, f"Hashcat encountered an error. Please contact a Mod for help.")
            return

        if os.path.exists(output_file):  
            with open(output_file, "r") as f:
                output = f.read().strip()
            if ':' in output:
                hash_value, cracked_password = output.split(':', 1)
                completion_message = f"{interaction.user.mention} - Cracked: `{cracked_password}` for hash `{hash_value}`"
                await interaction.channel.send(completion_message)
            else:
                await interaction.channel.send(content="Hashcat execution completed, but no passwords were cracked.")
        else:
            await interaction.channel.send(content="Hashcat execution completed, but no output file was generated.")
        
    except asyncio.TimeoutError:
        logging.error("Hashcat process timeout.")
        process.terminate()
        await interaction.channel.send("Hashcat took too long to respond. The process was terminated.")
    except Exception as e:
        logging.error(f"Unexpected error in execute_hashcat: {e}")
        await interaction.channel.send("An unexpected error occurred during hash cracking. Please contact RocketGod for help.")
    finally:
        os.chdir(original_cwd)

class aclient(discord.Client):
    is_busy = False 
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/hashcat")
        self.discord_message_limit = 2000

    async def send_split_messages(self, interaction, message: str, require_response=True):

        if not message.strip():
            logging.warning("Attempted to send an empty message.")
            return

        lines = message.split("\n")
        chunks = []
        current_chunk = ""

        for line in lines:
            if len(current_chunk) + len(line) + 1 > self.discord_message_limit:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk:
            chunks.append(current_chunk)

        if not chunks:
            logging.warning("No chunks generated from the message.")
            return

        if require_response and not interaction.response.is_done():
            await interaction.response.defer(ephemeral=False)

        try:
            await interaction.channel.send(content=chunks[0], ephemeral=False)
            chunks = chunks[1:]  
        except Exception as e:
            logging.error(f"Failed to send the first chunk via followup. Error: {e}")

        for chunk in chunks:
            try:
                await interaction.channel.send(chunk)
            except Exception as e:
                logging.error(f"Failed to send a message chunk to the channel. Error: {e}")

async def handle_errors(interaction, error, error_type="Error", cracked_password=None):
    if cracked_password:
        error_message = f"{error_type}: {error}\nCracked Password: {cracked_password}"
    else:
        error_message = f"{error_type}: {error}"
    logging.error(f"Error for user {interaction.user}: {error_message}")  
    
    # Send a generic error message to Discord
    try:
        if interaction.response.is_done():
            await interaction.channel.send("An error occurred while processing your request. Please try again later.")
        else:
            await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)
    except discord.HTTPException as http_err:
        logging.warning(f"HTTP error while responding to {interaction.user}: {http_err}")
    except Exception as unexpected_err:
        logging.error(f"Unexpected error while responding to {interaction.user}: {unexpected_err}")

def run_discord_bot(token):
    client = aclient()

    @client.event
    async def on_ready():
        await client.tree.sync()  # First sync
        logging.info(f'{client.user} is online.')
        await asyncio.sleep(5)  # Wait for 5 seconds
        await client.tree.sync()  # Second sync, just to ensure

    @client.tree.command(name="hashcat", description="Crack hashes using Hashcat")
    async def hashcat(interaction: discord.Interaction):
        if "options" not in interaction.data:
            await interaction.channel.send("You must provide required options.", ephemeral=True)
            return
        
        # Extract options from the interaction data
        options = {option["name"]: option["value"] for option in interaction.data["options"]}
        hash_value = options.get("hash")
        hashtype = options.get("hashtype")
        attack_mode = options.get("attack_mode")
        wordlist = options.get("wordlist", None)
        password_length = options.get("password_length", None)

        await interaction.response.send_message(f"Cracking `{hash_value}` for {interaction.user.mention} and will ping you when done.")

        # Validate the hash format
        if not re.match("^[a-fA-F0-9]+$", hash_value):
            await interaction.channel.send("Invalid hash format.", ephemeral=True)
            return

        # Check for unnecessary options based on attack mode
        if attack_mode == "dictionary" and password_length:
            await interaction.channel.send("You've provided a password length, but it's not needed for a dictionary attack.", ephemeral=True)
            return
        elif attack_mode == "bruteforce" and wordlist:
            await interaction.channel.send("You've provided a wordlist, but it's not needed for a bruteforce attack.", ephemeral=True)
            return

        # Assemble the arguments for hashcat
        args = [hashcat_exec]

        hash_type_mapping = {
            "md5": "0",
            "sha1": "100",
            "sha256": "1400",
            "sha512": "1700",
            "samsungandroid": "5800",
            "windowshello": "28100",
            "macos": "7100",  # Note: This is for macOS v10.8+. You may need to adjust based on specific versions.
            "bitlocker": "22100",
            "androidfde": "8800",  # Android FDE <= 4.3. You might need to differentiate between versions.
            "apfs": "18300",
            "pdf": "10700",  # PDF 1.7 Level 8 (Acrobat 10 - 11)
            "msoffice": "9600",  # MS Office 2013 as an example. You may need multiple mappings for different versions.
            "7zip": "11600",
            "rar": "13000",  # RAR5 as a representation. Adjust based on versions.
            "winzip": "13600",
            "itunes": "14800",  # iTunes backup >= 10.0. Adjust as needed.
            "telegram": "24500",  # Telegram Desktop >= v2.1.14 as an example.
            "skype": "23",
            "bitcoin": "11300",  # Bitcoin/Litecoin wallet.dat
            "ethereum": "15700"  # Ethereum Wallet with SCRYPT
        }

        args.extend(["-m", hash_type_mapping[hashtype]])

        # Ensure the output directory exists
        hashcat_dir = os.path.dirname(hashcat_exec)
        output_dir = os.path.abspath(os.path.join(hashcat_dir, "output"))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, f"{hash_value}.txt")

        # Add the attack mode and related arguments
        if attack_mode == "dictionary":
            args.append("-a")
            args.append("0")
            args.append(hash_value)
            if wordlist:
                args.append(wordlist)

        elif attack_mode == "bruteforce":
            args.append("-a")
            args.append("3")
            args.append(hash_value)
            if password_length:
                mask = "?a" * password_length
                args.append(mask)

        # Start the hashcat process in the background
        asyncio.create_task(execute_hashcat(interaction, args, output_file, hash_type_mapping, hashtype, hash_value))

    client.run(token)

if __name__ == "__main__":
    config = load_config()
    register_command.register_command()
    run_discord_bot(config.get("discord_bot_token"))

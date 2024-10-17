import psutil
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_system_details():
    try:
        public_ip = requests.get('https://ifconfig.me').text.strip()
    except requests.RequestException:
        public_ip = 'Unavailable'

    try:
        cpu_count = psutil.cpu_count(logical=False)
        logical_cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq().current

        ram_info = psutil.virtual_memory()
        total_ram = ram_info.total / (1024 ** 3)
        available_ram = ram_info.available / (1024 ** 3)

        current_process = psutil.Process()
        thread_count = current_process.num_threads()
    except Exception as e:
        cpu_count = logical_cpu_count = cpu_freq = total_ram = available_ram = thread_count = 'Unavailable'
        print(f"Error fetching system details: {e}")

    system_details = {
        "public_ip": public_ip,
        "current_time_ist": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "cpu_info": {
            "physical_cores": cpu_count,
            "logical_cores": logical_cpu_count,
            "current_frequency_mhz": cpu_freq
        },
        "ram_info": {
            "total_ram_gb": f"{total_ram:.2f} GB" if total_ram != 'Unavailable' else total_ram,
            "available_ram_gb": f"{available_ram:.2f} GB" if available_ram != 'Unavailable' else available_ram
        },
        "thread_info": {
            "thread_count": thread_count
        }
    }

    return system_details

def get_app_urls(ip_address):
    try:
        ports = [7000, 22, 9000, 8085, 3002]
        urls = [f"http://{ip_address}:{port}" for port in ports]
    except Exception as e:
        print(f"Error generating app URLs: {e}")
        urls = []
    
    return urls

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        details = get_system_details()
        app_urls = get_app_urls(details['public_ip'])

        message = (
            f"**Public IP:** {details['public_ip']}\n"
            f"**Current Time (IST):** {details['current_time_ist']}\n"
            f"**CPU Info:**\n"
            f"  - Physical Cores: {details['cpu_info']['physical_cores']}\n"
            f"  - Logical Cores: {details['cpu_info']['logical_cores']}\n"
            f"  - Current Frequency (MHz): {details['cpu_info']['current_frequency_mhz']}\n"
            f"**RAM Info:**\n"
            f"  - Total RAM: {details['ram_info']['total_ram_gb']}\n"
            f"  - Available RAM: {details['ram_info']['available_ram_gb']}\n"
            f"**Thread Info:**\n"
            f"  - Thread Count: {details['thread_info']['thread_count']}\n"
            f"**App URLs:**\n"
        )

        for idx, url in enumerate(app_urls, 1):
            message += f"  {idx}. {url}\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        print(f"Error in /start command: {e}")
        await update.message.reply_text("An error occurred while fetching system details.", parse_mode='Markdown')

def main():
    try:
        app = ApplicationBuilder().token("6293447468:AAHlxvdm0kQKR4aU2VFWENTB_4x4fDd4mjY").build()
        app.add_handler(CommandHandler("start", start))
        app.run_polling()
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(f"Main function error: {e}")

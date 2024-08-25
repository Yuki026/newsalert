import os
import re
import pytz
import json
import discord
from discord import SyncWebhook
from datetime import datetime
from config import WEEK, MONTH

news_path = "news.json"
data_path = "data.json"

def read(path):
    with open(path, "r") as file:
        return json.load(file)

def write(data):
    with open(data_path, "w") as file:
        json.dump(data, file, indent=4)

def create_flag(currency):
    if currency == "All":
        return "‎ " * 7
    return f":flag_{currency[:2].lower()}:"

def change_language(date):
    d = date.split(' ')
    return f"{WEEK[ d[0] ]}, {d[2]} {MONTH[ d[1] ]}"

def format_text(data):
    data_by_date = {}
    last = ""
    
    for item in data:
        day = change_language( item["date"] )
        time = item["time"].center(8, " ")

        if day not in data_by_date:
            data_by_date[day] = []
        
        if item["impact"] != "yellow" and item["impact"] != "orange" and item["greyed"] == "False":
            if time == last:
                time = " " * 8
            else:
                if ":" in time:
                    last = time

            data_by_date[day].append(
                f"`{time}`{create_flag(item['currency'])}  **{item['currency'].upper()}** - **{item['event']}**"
            )

    weekly = []
    start_day = False
    for day, events in data_by_date.items():
        if re.search("Sabtu", today) and not events:
            break
            
        if today == day or re.search("Minggu", today) or start_day:
            weekly.append(f":date: **{day}**\n")
            if not events:
                weekly.append("tidak ada news. <a:pepemoney1:1272102396239020074>")
            else:
                weekly.extend(events)
            weekly.append("\n﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋﹋")
            
            start_day = True
    return "\n".join(weekly)

def send_webhook(content, data):
    newData = {}
    webhook = SyncWebhook.from_url(
        os.environ["WEBHOOK_URL"]
        # "https://discord.com/api/webhooks/1274771477941719103/P2dIS_YDdiCvDvATxM47CgfAdL6VKJbkQwokhQ_KU3-oD8TczmHMr9JiFMPIKHNZE5Xe"
    )

    if "LAST_UPDATE" not in data:
        data["LAST_UPDATE"] = ""
        
    
    if re.search("Minggu", today) and data["LAST_UPDATE"] != today:
        try:
            if "MESSAGE_ID" in data:
                webhook.delete_message(data["MESSAGE_ID"])
        except discord.errors.NotFound:
            pass
        except TypeError:
            pass
        
        weekly = webhook.send(
            embed=discord.Embed(description=content, color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE'),
            wait=True,
        )

        data["MESSAGE_ID"] = weekly.id
        data["LAST_UPDATE"] = today
    elif not content:
        weekly = webhook.edit_message(data["MESSAGE_ID"],
            embed=discord.Embed(description="lagi nyari apa? <:wut:495217822780096532>", color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE')
        )
        data["MESSAGE_ID"] = data["MESSAGE_ID"]
        
    else:
        weekly = webhook.edit_message(data["MESSAGE_ID"],
            embed=discord.Embed(description=content, color=discord.Color.random()).set_footer(text='*Waktu: WIB (Asia/Jakarta)\n*Khusus berita dampak GEDE')
        )
        data["MESSAGE_ID"] = data["MESSAGE_ID"]

    return data

def main():
    data = read(data_path)
    content = format_text(read(news_path))
    newData = send_webhook(content, data)
    write(newData)

# now = datetime.now(pytz.timezone('Asia/Jakarta'))
now = datetime.strptime(os.environ["UPDATE_TIME"], "%Y-%m-%d %H:%M")
today = change_language( now.strftime("%a %b %-d") )

main()

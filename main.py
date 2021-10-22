import sys
import network
import machine
from time import sleep, localtime, time
from machine import Pin

# add custom libraries folder to root path
sys.path.insert(0, "/mylib")

from utelegram import Bot
from esp32_gpio_lcd import GpioLcd
from helpers import set_time, conv24h_12h, covid19

from config import utelegram_config, wifi_config

lcd_lines = 2
lcd_cols = 16

# init lcd
lcd = GpioLcd(rs_pin=Pin(13),
              enable_pin=Pin(12),
              d4_pin=Pin(26),
              d5_pin=Pin(25),
              d6_pin=Pin(33),
              d7_pin=Pin(32),
              num_lines=lcd_lines,
              num_columns=lcd_cols)

print("Connecting to WiFi...")
lcd.putstr("Connecting to\nWiFi...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()

if wlan.isconnected():
    wlan.disconnect()

try:
    wlan.connect(wifi_config["ssid"], wifi_config["password"])
except:
    print("Error: Couldn't connect to WiFi")
    lcd.clear()
    lcd.putstr("Error: Couldn't connect to WiFi")
    sys.exit()

while not wlan.isconnected():
    sleep(1)

print("WiFi connected\n\nSetting up bot...")
lcd.clear()
lcd.putstr("WiFi connected\nSetting up bot..")

bot = Bot(utelegram_config["token"])

lcd.clear()
lcd.putstr("Done!" + " "*(lcd_cols - len("Done!")) + "@lcdgram_bot") # \n isn't working for some reason
print("Bot is running...")

# list of paired ids in the session
paired_ids = []

# clock mode flags
clock_mode = False
time_synced = False
rtc = machine.RTC()

# covid-19 mode flags
covid_mode = False
covid = {}
covid_argument = ""
start_time = 0
covid_timer = machine.Timer(0)
covid_timer_counter = 0

help_msg = \
"""Commands:

/help: Show this message
/disp text: Display text
/clock: Turn on clock mode
/covid country: Turn on covid mode for a specific country\. Leave argument empty for world statistics
/clear: Clear display"""

@bot.add_message_handler(".*?")
def handler(update):
    # incoming message split into list
    msg = update.message["text"].split() 
    user_id = update.message["chat"]["id"]

    # that's alotta globals!
    global clock_mode, time_synced, rtc, covid_mode, covid, start_time, covid_timer, covid_argument, paired_ids

    # reset all flags if the command changes what's displayed on the lcd
    if not (msg[0] == "/start" or msg[0] == "/help" or msg[0] == "/pin"):
        clock_mode = False
        covid_mode = False
        covid_timer.deinit()

    if msg[0] == "/start":
        update.reply("Welcome to lcdgram\!\nAn IoT LCD controller using the Telegram bot API and an ESP32\.\nUse /pin to enter the pin and pair with the LCD\.")
        update.reply(help_msg)
        return None

    if msg[0] == "/pin":
        if user_id in paired_ids:
            update.reply("You are already paired\.")
            return None

        if len(msg) == 1:
            update.reply("Error: Incorrect usage\. Argument required\.")

        elif len(msg) > 2:
            update.reply("Error: Incorrect usage\. Only one argument required\.")

        else:
            if msg[1] == utelegram_config["pin"]:
                paired_ids.append(user_id)
                update.reply("Successfully paired\!")

            else:
                update.reply("Incorrect pin\.")

        return None

    # check if user is not paired
    if user_id not in paired_ids:
        update.reply("You are not paired with the device\. Use /pin to enter the pin and pair\.")
        return None

    if msg[0] == "/disp":
        if len(msg) == 1:
            update.reply("Error: Incorrect usage\. Argument required\.")
        else:
            text = " ".join(msg[1:])

            lcd.clear()
            lcd.putstr(text)
            
            update.reply("Message displayed\.")

            if len(text) > lcd_cols * lcd_lines:
                update.reply("Warning: Message is too large to fit your LCD\.")

    elif msg[0] == "/clock":
        clock_mode = True 

        # no need to sync the clock every time
        if not time_synced:
            lcd.clear()
            lcd.putstr("Synchronizing the clock...")

            rtc.init(set_time()) # note: the rtc documentation is completely messed up
            time_synced = True

        update.reply("Clock mode on\.")

    elif msg[0] == "/covid":
        covid_mode = True

        lcd.clear()
        lcd.putstr("Fetching COVID-19 data...")

        if len(msg) == 1:
            covid_argument = "world"
        elif len(msg) == 2:
            covid_argument = msg[1]
        else:
            update.reply("Error: invalid usage\.")

        try:
            covid = covid19(covid_argument)
            start_time = time()

            # set timer interrupt to cycle between deaths and cases
            covid_timer.init(period=5000, mode=machine.Timer.PERIODIC, callback=covid_disp)
            
            update.reply("COVID\-19 mode on\.")

        except:
            update.reply("Error: invalid argument\.")
            
            lcd.clear()
            lcd.putstr("Error: Invalid argument.")

    elif msg[0] == "/clear":
        lcd.clear()
        update.reply("Display cleared\.")

    elif msg[0] == "/help":
        update.reply(help_msg)

    else:
        update.reply("Error: Invalid command\.\nType /help for a list of the available commands\.")

# timer interrupt handler to cycle between deaths and cases
def covid_disp(timer):
    global covid_timer_counter

    if covid_timer_counter % 2 == 0:
        stat = "cases"
    else:
        stat = "deaths"

    spaces = lcd_cols - len("COVID-19") - len(covid["country"])

    lcd.clear()
    lcd.putstr("COVID-19" +" "*spaces + covid["country"].upper() + stat + ": " + covid[stat])
    covid_timer_counter += 1

def clock():
    (hour, ampm) = conv24h_12h(localtime()[3])
    minute = str(localtime()[4])

    day = str(localtime()[2])
    month = str(localtime()[1])
    year = str(localtime()[0])

    # zero padding
    if len(hour) < 2:
        hour = "0" + hour
    if len(minute) < 2:
        minute = "0" + minute
    if len(day) < 2:
        day = "0" + day
    if len(month) < 2:
        month = "0" + month

    offset_h = int((lcd_cols - 8)/2) # time centering offset
    offset_d = int((lcd_cols - 10)/2) # date centering offset

    lcd.clear()
    lcd.putstr(" "*offset_h + hour + ":" + minute + " " + ampm + " "*(offset_h+offset_d) + day + "-" + month + "-" + year)

while True:
    if clock_mode:
        clock()

    if covid_mode and (time() - start_time) >= 60*15:
        covid = covid19(covid_argument)
        start_time = time()

    bot.read_once()

import requests, json, threading, telebot, RPi.GPIO as GPIO
from telebot import types

# Weather API settings
api_key = "YOUR_OPENWEATHERMAP_API"
base_url = "http://api.openweathermap.org/data/2.5/weather?"
city_name = "Aachen"
complete_url = base_url + "appid=" + api_key + "&q=" + city_name

# GPIO Settings
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
relais = 27
GPIO.setup(relais, GPIO.OUT)
GPIO.output(relais, GPIO.LOW)

# Telebot API settings
TOKEN = 'YOUR_TOKEN_FOR_TELEGRAM_BOT'
bot = telebot.TeleBot(TOKEN)

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
button_on10 = types.KeyboardButton(text='Airing on for 10 min')
button_on = types.KeyboardButton(text='Airing on')
button_off = types.KeyboardButton(text='Airing off')
keyboard.add(button_on10, button_on, button_off)


def req_weather():
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":  # "404", means city is found otherwise
        # store the value of "main"
        # key in variable y
        y = x["main"]

        current_temperature = int(y["temp"] - 273.15)
        current_humidiy = int(y["humidity"])

        # print following values
        outside = " Outside: " + str(current_temperature) + "°C, " + str(current_humidiy) + "% hmd"
        print(outside)
        return outside
    else:
        error = " Current weather for the city is not found "
        print(error)
        return error


def socket_off():
    GPIO.output(relais, GPIO.LOW)
    print("off")


def socket_on():
    GPIO.output(relais, GPIO.HIGH)
    print("on")


def socket_timer(minutes):
    socket_on()
    timer = threading.Timer(minutes * 60, socket_off)
    timer.start()
    print("timer started")


@bot.message_handler(func=lambda message: message.text == 'Airing on for 10 min')
def send_confirm_timer(message):
    socket_timer(10)
    bot.send_message(message.chat.id, 'Airing turned on for 10 minutes')
    weather = req_weather()
    bot.send_message(message.chat.id, weather)


@bot.message_handler(func=lambda message: message.text == 'Airing on')
def send_confirm_on(message):
    socket_on()
    bot.send_message(message.chat.id, 'Airing turned on')
    weather = req_weather()
    bot.send_message(message.chat.id, weather)


@bot.message_handler(func=lambda message: message.text == 'Airing off')
def send_confirm_off(message):
    socket_off()
    bot.send_message(message.chat.id, 'Airing turned off')
    weather = req_weather()
    bot.send_message(message.chat.id, weather)


@bot.message_handler(commands='start')
def send_keyboard(message):
    bot.send_message(message.chat.id, 'Choose one option', reply_markup=keyboard)


bot.polling()

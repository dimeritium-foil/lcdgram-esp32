# lcdgram

## Demo

[![Demo video on YouTube.](https://img.youtube.com/vi/MZYB17NEYmU/0.jpg)](https://www.youtube.com/watch?v=MZYB17NEYmU)

## Libraries Used

* [python_lcd](https://github.com/dhylands/python_lcd)
* [telegram-upy](https://github.com/gabrielebarola/telegram-upy)

Many thanks to the creators of these projects.

## Usage

Rename `config.py-demo` to `config.py` and a replace the placeholders with your credentials and the pin code you want, and before you upload all the files to your ESP32 don't forget to configure the your LCD's dimensions and pins (and your bot's name) in `main.py`.

Here is the list of available bot commands with a description of each:

1. /help: Sends the list of available commands with a short description of each one.
2. /pin pincode: This is used to pair with the display.
3. /disp text: Will display whatever the text the user enters after it on the LCD.
4. /clock: Turn clock mode on, where it will synchronize the internal RTC using a web
API (timeapi.io) and display the current time and date on the LCD and update them
continuously.
5. /covid country: Turns on COVID-19 mode where it will display the cases and deaths for
the chosen country. If country is left empty it will display the global statistics. The data is
updated regularly every 15 minutes, and is fetched from a reliable API (disease.sh).
6. /clear: Clears the display.

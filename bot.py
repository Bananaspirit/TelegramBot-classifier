from time import sleep
import telebot
import io
from procesing_image_func import resize_image
import prediction_func as pf
from prediction_func import percent, predict_image

bot = telebot.TeleBot('YOUR_TOKEN')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!\nЯ бот классификатор!\nОтправь мне изображение овоща из данных классов: огурец, помидор, салат(латук), болгарский перец.\nРекомендация: для корректной работы бота на изображении должен быть один овощ.')

@bot.message_handler(content_types=['photo'])
def handle_save_photo(message):

    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image=io.BytesIO(downloaded_file)
    bot.reply_to(message, "Обрабатываю изображение...")
    sleep(1)

    r_image = resize_image(image)

    prdct = predict_image(r_image,pf.model)
    per = percent(r_image,pf.model)

    if prdct == "cucumber" and per > 99.999:
        bot.reply_to(message, "На изображении огурец")
    elif prdct == "tomato" and per > 99.9:
        bot.reply_to(message, "На изображении помидор")
    elif prdct == "lettuce" and per > 99.99:
        bot.reply_to(message, "На изображении салат")
    elif prdct == "pepper" and per > 99.99:
        bot.reply_to(message, "На изображении болгарский перец")
    else:
        bot.reply_to(message,"Пожалуйста загрузите изображение из классов которые знает бот!\nКлассы: огурец, помидор, салат(латук), болгарский перец")
bot.polling()

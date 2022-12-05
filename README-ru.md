<h1 align="center"><a href="https://t.me/fruits_vegetables_sx_bot" target="_blank">TelegramBot-classifier</a> 

Этот проект направлен на демонстрацию того как внедрять обученные предиктивные модели нейросетей в Телеграм ботов.

## Введение

### В качестве площадки для тестирования и внедрения предиктивной модели я использовал Telegram, популярная площадка во всем мире, которая позволяет создавать ботов бесплатно. Так же я использовал Kaggle для тестирования различных готовых моделей и обучения своей. 

## Сбор и обработка данных

### В качестве набора данных я использовал яндекс-картинки для 4-х классов (помидор, огурец, болгарский перец, салат-латук). Картинки я парсил с помощью [этого сайта](https://appscyborg.com). Конечно же там было много мусора, от которого нужно было избавиться, чтобы не запороть обучение.
<img src="/data_test/test/tomato/tomato701.png"> <img src="/data_test/test/cucumber/cucumber704.png"> <img src="/data_test/test/lettuce/lettuce704.png"> 
<img src="/data_test/test/pepper/pepper703.png">
### Ненужные картинки удалялись в основном по расширениям, в интернете можно найти много примеров как автоматизированно удалить все файлы с определенным расширением, [пример](https://stackoverflow.com/questions/1995373/deleting-all-files-in-a-directory-with-python). После того как папка с картинками очищена от мусора их можно переименовать, но это не обязательно, лишь для удобства дальнейшей разработки, [пример](https://www.cyberforum.ru/python-beginners/thread2817242.html). Далее все картинки необходимо привести к единой размерности для обучения нейросети, пример:
```Python
from PIL import Image

def resize_image(save_image):
        try:
            image = Image.open(save_image)
            return image.resize((224,224), Image.ANTIALIAS)
        except Exception:
            pass
```

## Обучение

### После того как датасет сформирован идем на kaggle и ищем подходящий нам блокнот с кодом, после недолгих поисков я нашел [блокнот](https://www.kaggle.com/code/theeyeschico/vegetable-classification-using-transfer-learning), где пользователь использует метод Transfer-learning на основе предобученной модели Inception-V3 на наборе данных ImageNet. На kaggle мы загружаем свой датасет, в блокноте прописываем свои пути к папкам с изображениями и запускаем обучение. Так же вы можете поиграться с настройками сети, для получения наилучшей метрики accuracy. На выходе мы получаем файл с весами обученной модели с расширением file_name.h5, этот файл мы будем в дальнейшем использовать в теле бота.

## Создание бота

### Процесс создания самого бота довольно тривиальный и подробно описан [здесь](https://habr.com/ru/post/442800/), верстать бота будем на python с помощью pyTelegramBotAPI. После создания бота в Телеграм получаем токен, который нужен для связи локальной машины с сервером Телеграм. В python-файле импортируем библиотеку pyTelegramBotAPI и подключаем токен бота.
```Python
import telebot
bot = telebot.TeleBot('%ваш токен%')
```
### Объявим метод для обработки команды /start.
```Python
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!\nЯ бот классификатор!\nОтправь мне изображение овоща из данных классов: огурец, помидор, салат(латук), болгарский перец.\nРекомендация: для корректной работы бота на изображении должен быть один овощ.')
```
### Объявим метод для обработки команды 'photo'.
```Python
@bot.message_handler(content_types=['photo'])
def handle_save_photo(message):
    pass
```
### В этом блоке начинается основная часть нашего бота. Когда пользователь отправляет в бота изображение его необходимо сохранить на устройстве, что очень неудобно для такого маленького бота - реализовывать полноценное хранилище для всех изображений. Я же пошел по другому пути, сохранять изображение в буфер обмена (память устройства). Таким образом мы не забиваем хранилище и не мучаемся с сохранением и использованием изображения из папки.
```Python
file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
downloaded_file = bot.download_file(file_info.file_path)
image=io.BytesIO(downloaded_file)
bot.reply_to(message, "Обрабатываю изображение...")
```
### Далее разберемся с тремя основными функциями которые меняют размер изображений, вовзращют класс объекта на изображении и процент точности.
```Python
r_image = resize_image(image)
prdct = predict_image(r_image,pf.model)
per = percent(r_image,pf.model)
```
### Функция resize_image() импортируется из файла procesing_image_func.py, в качестве аргумента принимает массив пикселей в виде списка Numpy. Это наше изображение которое нужно урезать до размера 224х224.
```Python
from PIL import Image

def resize_image(save_image):
        try:
            image = Image.open(save_image)
            return image.resize((224,224), Image.ANTIALIAS)
        except Exception:
            pass
```
### Функция predict_image() импортируется из файла prediction_func.py, в качестве аргументов в функцию необходимо передать измененное изображение и обученную модель, которую мы скачали с kaggle. На выходе мы получим класс на изображении.
```Python
category={0: 'cucumber', 1: 'lettuce', 2: 'pepper', 3 : 'tomato'}

def predict_image(filename,model):
    img_array = image.img_to_array(filename)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)
    index = np.argmax(prediction)
    return category[index]
```
### Функция percent() импортируется из файла prediction_func.py, в качестве аргументов в функцию необходимо передать измененное изображение и обученную модель, которую мы скачали с kaggle. На выходе мы получаем значение в процентах, для корректировки точности модели.
```Python
def percent(filename,model):
    img_array = image.img_to_array(filename)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)
    return 100*np.max(prediction)
```
### Ну и завершеющий штрих бота, из функции мы получаем класс и его процент, уже из этих параметров мы можем сделать простой фильтр для изображений которые не относятся к нашим классам, например фото Папы Римского.
![440426](https://user-images.githubusercontent.com/106806088/205707538-5bb2d363-da4b-4095-818b-65958f6ae636.jpg)
```Python
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
```

### Заключение

### В заключение хочу сказать что данный проект был сделан исключительно из личного интереса, что нзывается пощупать тонкости разработки Телеграм ботов с применением алгоритмов машинного обучения, а если точнее нейросетей. Так же ценность этого проекта для меня так и для других пользователей в том, что на интернет пространстве практически нет таких проектов в открытом доступе.



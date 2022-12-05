<h1 align="center"><a href="https://t.me/fruits_vegetables_sx_bot" target="_blank">TelegramBot-classifier</a> 

This project is aimed at demonstrating how to implement trained predictive neural network models in Telegram bots.

## Introduction

### As a platform for testing and implementing a predictive model, I used Telegram, a popular platform around the world that allows you to create bots for free. I also used Kaggle to test various ready-made models and train my own. 

## Data collection and processing

### As a data set, I used yandex images for 4th grades (tomato, cucumber, bell pepper, lettuce). I parsed the pictures using [this site](https://appscyborg.com). Of course, there was a lot of garbage that had to be disposed of so as not to mess up the training.
<img src="/data_test/test/tomato/tomato701.png"> <img src="/data_test/test/cucumber/cucumber704.png"> <img src="/data_test/test/lettuce/lettuce704.png"> 
<img src="/data_test/test/pepper/pepper703.png">
### Unnecessary images were deleted mainly by extensions, on the Internet you can find many examples of how to automatically delete all files with a certain extension, [example](https://stackoverflow.com/questions/1995373/deleting-all-files-in-a-directory-with-python). After the folder with pictures is cleared of garbage, they can be renamed, but this is not necessary, just for the convenience of further development, [example](https://www.cyberforum.ru/python-beginners/thread2817242.html). Next, all images must be brought to a single dimension for training a neural network, for example:
```Python
from PIL import Image

def resize_image(save_image):
        try:
            image = Image.open(save_image)
            return image.resize((224,224), Image.ANTIALIAS)
        except Exception:
            pass
```

## Training

### After the dataset is formed, we go to kaggle and look for a notebook with the code that suits us, after a short search I found [notepad](https://www.kaggle.com/code/theeyeschico/vegetable-classification-using-transfer-learning ), where the user uses the Transfer-learning method based on the pre-trained Inception-V3 model on the ImageNet dataset. We upload our dataset to kaggle, write our paths to the folders with images in notepad and start training. You can also play around with the network settings to get the best accuracy metric. At the output, we get a file with the weights of the trained model with the file_name.h5 extension, we will use this file in the body of the bot in the future.

## Creating a bot

### The process of creating the bot itself is quite trivial and described in detail [here](https://habr.com/ru/post/442800), we will make up the bot in python using pyTelegramBotAPI. After creating a bot in Telegram, we get a token that is needed to connect the local machine with the Telegram server. In the python file, import the pyTelegramBotAPI library and connect the bot token.
```Python
import telebot
bot = telebot.TeleBot('%ваш токен%')
```
### Declare a method for processing the /start command.
```Python
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!\nЯ бот классификатор!\nОтправь мне изображение овоща из данных классов: огурец, помидор, салат(латук), болгарский перец.\nРекомендация: для корректной работы бота на изображении должен быть один овощ.')
```
### Declare a method for processing the 'photo' command.
```Python
@bot.message_handler(content_types=['photo'])
def handle_save_photo(message):
    pass
```
### The main part of our bot starts in this block. When a user sends an image to the bot, it needs to be saved on the device, which is very inconvenient for such a small bot - to implement a full-fledged storage for all images. I went the other way, save the image to the clipboard (device memory). This way we do not clog the storage and do not suffer with saving and using the image from the folder.
```Python
file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
downloaded_file = bot.download_file(file_info.file_path)
image=io.BytesIO(downloaded_file)
bot.reply_to(message, "Обрабатываю изображение...")
```
### Next, let's look at the three main functions that change the size of images, returns the class of the object in the image and the percentage of accuracy.
```Python
r_image = resize_image(image)
prdct = predict_image(r_image,pf.model)
per = percent(r_image,pf.model)
```
### The resize_image() function is imported from a file procesing_image_func.py , takes as an argument an array of pixels in the form of a Numpy list. This is our image that needs to be trimmed to a size of 224x224.
```Python
from PIL import Image

def resize_image(save_image):
        try:
            image = Image.open(save_image)
            return image.resize((224,224), Image.ANTIALIAS)
        except Exception:
            pass
```
### The predict_image() function is imported from a file prediction_func.py , as arguments to the function, it is necessary to pass the modified image and the trained model that we downloaded from kaggle. At the output, we will get a class in the image.
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
### The percent() function is imported from a file prediction_func.py , as arguments to the function, it is necessary to pass the modified image and the trained model that we downloaded from kaggle. At the output, we get a percentage value to adjust the accuracy of the model.
```Python
def percent(filename,model):
    img_array = image.img_to_array(filename)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)
    return 100*np.max(prediction)
```
### Well, the finishing touch of the bot, from the function we get the class and its percentage, already from these parameters we can make a simple filter for images that do not belong to our classes, for example, a photo of the Pope.
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
### Conclusion

### In conclusion, I want to say that this project was made solely out of personal interest, which is called to feel the subtleties of developing Telegram bots using machine learning algorithms, or more precisely neural networks. Also, the value of this project for me and for other users is that there are practically no such projects in the open access on the Internet.














































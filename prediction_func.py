import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

path_to_model='predict_models/model_inceptionV3_epoch10.h5'
model = load_model(path_to_model)

category={0: 'cucumber', 1: 'lettuce', 2: 'pepper', 3 : 'tomato'}

def predict_image(filename,model):
    img_array = image.img_to_array(filename)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)
    index = np.argmax(prediction)
    return category[index]

def percent(filename,model):
    img_array = image.img_to_array(filename)
    img_processed = np.expand_dims(img_array, axis=0)
    img_processed /= 255.

    prediction = model.predict(img_processed)
    return 100*np.max(prediction)

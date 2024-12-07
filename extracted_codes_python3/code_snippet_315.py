import keras
from tensorflow import data as tf_data
import tensorflow as tf
from keras import Sequential
from keras_cv import layers
import keras
import numpy as np
from matplotlib import pyplot as plt
from sympy.stats.sampling.sample_numpy import numpy
import os
from PIL import Image



num_skipped = 0
parent_folders = ['../dataset/training_set','../dataset/test_set']

for each_folder in parent_folders:
    for folder_name in ("cats", "dogs"):
        folder_path = os.path.join(each_folder, folder_name)
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            try:
                fobj = open(fpath, "rb")
                is_jfif = b"JFIF" in fobj.peek(10)
            finally:
                fobj.close()

            if not is_jfif:
                num_skipped += 1
                # Delete corrupted image
                os.remove(fpath)

    print(f"Deleted {num_skipped} images.")




preprocessing_layers_train = Sequential([
    layers.Rescaling(1./255),
    layers.RandomShear(0.2),
    layers.RandomZoom(0.2),
    layers.RandomFlip("horizontal")
])
preprocessing_layer_test = Sequential([layers.Rescaling(1./255)])

train_dataset = keras.utils.image_dataset_from_directory('../dataset/training_set',
                                         image_size=(64, 64),
                                         batch_size=None,
                                         label_mode='binary')
test_dataset = keras.utils.image_dataset_from_directory('../dataset/test_set',
                                         image_size=(64, 64),
                                         batch_size=None,
                                         label_mode='binary'
                                                        )

train_dataset_batch = train_dataset.batch(32, drop_remainder=True)
test_dataset_batch = test_dataset.batch(32, drop_remainder=True)


train_set = train_dataset_batch.map(lambda x,y:(preprocessing_layers_train(x),y))
test_set = test_dataset_batch.map(lambda x,y:(preprocessing_layer_test(x),y))

# def filter_function(image, label):
#     res = tf.shape(image)[1] == 64 and tf.shape(image)[2] == 64 and tf.shape(image)[-1] == 3
#     # Keep only elements where the image shape is 64x64x3
#     return res
#
# # Apply filter to remove unwanted elements
# filtered_dataset = test_set.filter(filter_function)
#
# for idx,(images, labels) in enumerate(test_set):
#     print("Test Images Shape:", images.shape)
#     print("Test Labels Shape:", labels.shape)
#     if images.shape != (32,64, 64, 3):
#         print(images.shape[1:])



# for images, labels in train_set.take(1):
#     print(labels)
#     plt.figure(figsize=(10,10))
#     for i in range(9):
#         ax = plt.subplot(3,3,i+1)
#         plt.imshow(images[i].numpy())
#         plt.gray()
#         ax.get_xaxis().set_visible(False)
#         ax.get_yaxis().set_visible(False)
#     plt.show()
#
# for images, labels in test_set.take(1):
#     print(labels)
#     plt.figure(figsize=(10,10))
#     for i in range(9):
#         ax = plt.subplot(3,3,i+1)
#         plt.imshow(images[i].numpy())
#         plt.gray()
#         ax.get_xaxis().set_visible(False)
#         ax.get_yaxis().set_visible(False)
#     plt.show()


#Building CNN

# cnn = Sequential()
# cnn.add(keras.Input(shape=(64,64,3)))
# cnn.add(keras.layers.Conv2D(filters=32, kernel_size=3, activation='relu'))
# cnn.add(keras.layers.MaxPooling2D(pool_size=2, strides=2))
# cnn.add(keras.layers.Conv2D(filters=64, kernel_size=3, activation='relu'))
# cnn.add(keras.layers.MaxPooling2D(pool_size=2, strides=2))
# cnn.add(keras.layers.Flatten())
# cnn.add(keras.layers.Dense(units=64, activation='relu'))
# cnn.add(keras.layers.Dense(units=1, activation='sigmoid'))
# cnn.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# for images,labels in train_set.take(1):
#     print(images.shape)
#     print(images.dtype)
#     print(labels.shape)
#     print(labels.dtype)
# for images,labels in test_set.take(1):
#     print(images.shape)
#     print(images.dtype)
#     print(labels.shape)
#     print(labels.dtype)
# cnn.fit(train_set,validation_data=test_set,epochs=25,)

#Testing the CNN

#keras.saving.save_model(cnn, '../models/cnn.keras')
load_model = keras.models.load_model('../models/cnn.keras')

#Get the image from image directory

def test_model(file_path,model,train_dataset):
    img_1 = keras.utils.load_img(file_path, target_size=(64, 64))
    img_1_to_arry = keras.utils.img_to_array(img_1)
    img_1_added_dim = img_1_to_arry[np.newaxis]
    result = model.predict(img_1_added_dim)
    plt.figure(figsize=(4, 4))
    plt.imshow(Image.open(file_path))
    plt.title(train_dataset.class_names[result.astype(int).tolist()[0][0]])
    plt.show()
test_model('../dataset/single_prediction/cat_or_dog_1.jpg',load_model,train_dataset)
test_model('../dataset/single_prediction/cat_or_dog_2.jpg',load_model,train_dataset)






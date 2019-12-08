# -*- coding: utf-8 -*-
"""“cnn.ipynb”的副本

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MVAcsgNwgivYRzHQCZQ8HPVhI3MWttPr

##### Copyright 2019 The TensorFlow Authors.
"""

#@title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""# Convolutional Neural Network (CNN)

<table class="tfo-notebook-buttons" align="left">
  <td>
    <a target="_blank" href="https://www.tensorflow.org/tutorials/images/cnn">
    <img src="https://www.tensorflow.org/images/tf_logo_32px.png" />
    View on TensorFlow.org</a>
  </td>
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/tutorials/images/cnn.ipynb">
    <img src="https://www.tensorflow.org/images/colab_logo_32px.png" />
    Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/tensorflow/docs/blob/master/site/en/tutorials/images/cnn.ipynb">
    <img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />
    View source on GitHub</a>
  </td>
  <td>
    <a href="https://storage.googleapis.com/tensorflow_docs/docs/site/en/tutorials/images/cnn.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" />Download notebook</a>
  </td>
</table>

This tutorial demonstrates training a simple [Convolutional Neural Network](https://developers.google.com/machine-learning/glossary/#convolutional_neural_network) (CNN) to classify [CIFAR images](https://www.cs.toronto.edu/~kriz/cifar.html). Because this tutorial uses the [Keras Sequential API](https://www.tensorflow.org/guide/keras/overview), creating and training our model will take just a few lines of code.

### Import TensorFlow
"""

#%%
# Commented out IPython magic to ensure Python compatibility.
from __future__ import absolute_import, division, print_function, unicode_literals

# Import explainer and callback

from tf_explain.core.grad_cam import GradCAM

from tf_explain.callbacks.grad_cam import GradCAMCallback

# try:
#   # %tensorflow_version only exists in Colab.
# #   %tensorflow_version 2.x
# except Exception:
#   pass

import tensorflow as tf
# keras = tf.keras

from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dense, Concatenate, Flatten, concatenate
# from tensorflow import keras

# from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import hdf5storage as hdf5storage
import numpy as np

from IPython.display import SVG

import os
from tensorflow.keras.utils import model_to_dot
from tensorflow.keras.utils import plot_model

tf.keras.backend.set_image_data_format('channels_last')



#%%
file_name = 'dataset_10017_reshaped.mat'
data_raw = hdf5storage.loadmat(file_name)
images = data_raw['img']
# images = images[:, :, :, 0]
# images = np.expand_dims(images, axis=-1)
labels = data_raw['label']
print(labels.dtype)
labels = labels.astype('uint8')
labels = labels - 1
print(labels.dtype)

width_image = 100  # width of images
num_classes = 7

# randomization
randseed = 1
np.random.seed(randseed)
images_number = images.shape[0]
ind_randomized = np.random.permutation(images_number)
images = images[ind_randomized]
labels = labels[ind_randomized]

ratio_train = 0.5
ind_cutoff = np.ceil(images_number * ratio_train).astype("int")

images_train = images[0:ind_cutoff]
labels_train = labels[0:ind_cutoff]
images_vali = images[ind_cutoff:]
labels_vali = labels[ind_cutoff:]


# verify the images and labels are correct
plt.figure(figsize=(10,10))
for m in range(9):
    plt.subplot(3, 3, m + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(images_train[m, :, :, 0], cmap='gray')
    plt.xlabel('%d' % labels_train[m])
plt.show()

plt.figure(figsize=(10,10))
for m in range(9):
    plt.subplot(3, 3, m + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(images_vali[m, :, :, 0], cmap='gray')
    plt.xlabel('%d' % labels_vali[m])
plt.show()

#%%

"""### Create the convolutional base

The 6 lines of code below define the convolutional base using a common pattern: a stack of [Conv2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D) and [MaxPooling2D](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPool2D) layers.

As input, a CNN takes tensors of shape (image_height, image_width, color_channels), ignoring the batch size. If you are new to these dimensions, color_channels refers to (R,G,B). In this example, you will configure our CNN to process inputs of shape (32, 32, 3), which is the format of CIFAR images. You can do this by passing the argument `input_shape` to our first layer.
"""

def model(data_input1, data_input2, data_input3, data_output):

    # input layer
    input_time = Input(shape=(width_image, width_image, 1), name='Input_time')
    input_freq = Input(shape=(width_image, width_image, 1), name='Input_freq')
    input_recc = Input(shape=(width_image, width_image, 1), name='Input_recc')

    conv_time_1 = Conv2D(32, (3, 3), activation='relu', input_shape=(width_image, width_image, 1), name='Conv_time_1')(input_time)
    maxpool_time_1 = MaxPooling2D((2, 2), name='Maxpool_time_1')(conv_time_1)
    conv_time_2 = Conv2D(64, (3, 3), activation='relu', name='Conv_time_2')(maxpool_time_1)
    maxpool_time_2 = MaxPooling2D((2, 2), name='Maxpool_time_2')(conv_time_2)
    conv_time_3 = Conv2D(64, (3, 3), activation='relu', name='Conv_time_3')(maxpool_time_2)
    # print(conv_time_3.output_shape)

    conv_freq_1 = Conv2D(32, (3, 3), activation='relu', input_shape=(width_image, width_image, 1), name='Conv_freq_1')(input_freq)
    maxpool_freq_1 = MaxPooling2D((2, 2), name='Maxpool_freq_1')(conv_freq_1)
    conv_freq_2 = Conv2D(64, (3, 3), activation='relu', name='Conv_freq_2')(maxpool_freq_1)
    maxpool_freq_2 = MaxPooling2D((2, 2), name='Maxpool_freq_2')(conv_freq_2)
    conv_freq_3 = Conv2D(64, (3, 3), activation='relu', name='Conv_freq_3')(maxpool_freq_2)
    # print(conv_freq_3.output_shape)

    conv_recc_1 = Conv2D(32, (3, 3), activation='relu', input_shape=(width_image, width_image, 1), name='Conv_recc_1')(input_recc)
    maxpool_recc_1 = MaxPooling2D((2, 2), name='Maxpool_recc_1')(conv_recc_1)
    conv_recc_2 = Conv2D(64, (3, 3), activation='relu', name='Conv_recc_2')(maxpool_recc_1)
    maxpool_recc_2 = MaxPooling2D((2, 2), name='Maxpool_recc_2')(conv_recc_2)
    conv_recc_3 = Conv2D(64, (3, 3), activation='relu', name='Conv_recc_3')(maxpool_recc_2)
    # print(conv_recc_3.output_shape)

    # merged = Concatenate(axis=-1)([conv_time_3, conv_freq_3, conv_recc_3])
    merged = concatenate([conv_time_3, conv_freq_3, conv_recc_3], axis=-1, name='Merged')  # , axis=-1, name='Merged'
    # merged = Concatenate(axis=-1, name='Merged')([conv_time_3, conv_freq_3, conv_recc_3])
    merged = Flatten()(merged)

    dense_1 = Dense(64, activation='relu', name='Dense_1')(merged)
    output = Dense(num_classes, activation='softmax')(dense_1)
    model = tf.keras.models.Model(inputs=[input_time, input_freq, input_recc], outputs=[output])

    return model


data_input1 = np.expand_dims(images_train[:, :, :, 0], axis=-1)
data_input2 = np.expand_dims(images_train[:, :, :, 1], axis=-1)
data_input3 = np.expand_dims(images_train[:, :, :, 2], axis=-1)
data_output = labels_train

data_input1_vali = np.expand_dims(images_vali[:, :, :, 0], axis=-1)
data_input2_vali = np.expand_dims(images_vali[:, :, :, 1], axis=-1)
data_input3_vali = np.expand_dims(images_vali[:, :, :, 2], axis=-1)
data_output_vali = labels_vali

model = model(data_input1, data_input2, data_input3, data_output)

model.summary()

if not os.path.exists('model.png'):
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)

SVG(model_to_dot(model).create(prog='dot', format='svg'))


#%%

# model = keras.models.Sequential()
# model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(width_image, width_image, 1), name='conv1'))
# model.add(keras.layers.MaxPooling2D((2, 2), name='maxpool1'))
# model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', name='conv2'))
# model.add(keras.layers.MaxPooling2D((2, 2), name='maxpool2'))
# model.add(keras.layers.Conv2D(64, (3, 3), activation='relu', name='conv3'))
#
# """Let's display the architecture of our model so far."""
#
# model.summary()
#
# """Above, you can see that the output of every Conv2D and MaxPooling2D layer is a 3D tensor of shape (height, width, channels). The width and height dimensions tend to shrink as you go deeper in the network. The number of output channels for each Conv2D layer is controlled by the first argument (e.g., 32 or 64). Typically,  as the width and height shrink, you can afford (computationally) to add more output channels in each Conv2D layer.
#
# ### Add Dense layers on top
# To complete our model, you will feed the last output tensor from the convolutional base (of shape (3, 3, 64)) into one or more Dense layers to perform classification. Dense layers take vectors as input (which are 1D), while the current output is a 3D tensor. First, you will flatten (or unroll) the 3D output to 1D,  then add one or more Dense layers on top. CIFAR has 10 output classes, so you use a final Dense layer with 10 outputs and a softmax activation.
# """
#
# model.add(keras.layers.Flatten())
# model.add(keras.layers.Dense(64, activation='relu'))
# model.add(keras.layers.Dense(7, activation='softmax'))
#
# """Here's the complete architecture of our model."""
#
# model.summary()
#
# # callbacks = [
# #     GradCAMCallback(
# #         validation_data=(test_images, test_labels),
# #         layer_name="activation_1",
# #         class_index=0,
# #         output_dir=output_dir,
# #     )
# # ]
#
# """As you can see, our (3, 3, 64) outputs were flattened into vectors of shape (576) before going through two Dense layers.
#
# ### Compile and train the model
# """

#%%

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(x=[data_input1, data_input2, data_input3], y=[data_output], epochs=2, verbose=1,
                    validation_data=([data_input1_vali, data_input2_vali, data_input3_vali], [data_output_vali]))  # , callbacks=callbacks

"""### Evaluate the model"""

plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0.5, 1])
plt.legend(loc='lower right')

test_loss, test_acc = model.evaluate(x=[data_input1_vali, data_input2_vali, data_input3_vali], y=[data_output_vali], verbose=1)

print(test_acc)

"""Our simple CNN has achieved a test accuracy of over 70%. Not bad for a few lines of code! For another CNN style, 
see an example using the Keras subclassing API and a `tf.GradientTape` 
[here](https://www.tensorflow.org/tutorials/quickstart/advanced)."""


#%%
# Instantiation of the explainer
explainer = GradCAM()
channel_to_explain = 0

for class_index in range(7):
    ind_in_images_vali = np.where(labels_vali == class_index)[0]

    img_explain1 = data_input1_vali[ind_in_images_vali[0:25], :, :, :]
    img_explain2 = data_input2_vali[ind_in_images_vali[0:25], :, :, :]
    img_explain3 = data_input3_vali[ind_in_images_vali[0:25], :, :, :]

    data = ([img_explain1, img_explain2, img_explain3], None)

    # Save output
    output_dir = '.'
    output_name = 'grad_cam_class_%d_channel_%d.png' % (class_index, channel_to_explain)

    name_of_conv = 'Conv_time_3'

    output = explainer.explain(data, model, name_of_conv, class_index)
    explainer.save(output, output_dir, output_name)


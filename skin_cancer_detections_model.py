# -*- coding: utf-8 -*-
"""Skin_Cancer_Detections_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18psOUvZw3_VNAJ4-WdU1wVJhPKS1LV6t

# **Submitted By Gurpreet Singh😊**

#**Final Stage**
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow
from tensorflow.keras import backend as k
from tensorflow import keras

## loded our file into csv format
def append_path(df,path):## decorator
  ## append only jpg files
  def append_txt(fn):
    return fn+".jpg";
  df["image"]=df["image"].apply(append_txt)
  print("DataFrame Head:\n",df["image"].head())

# Name: image, dtype: object
# Updated DF with Extensions and Path:
#  /content/512x512/ISIC_2637011.jpg
  ## Append Absolute file path to where the image are located
  abs_file_names=[]
  for file_name in df["image"]:
    tmp=path+"/"+file_name
    abs_file_names.append(tmp)
  df["image"]=abs_file_names
  print("Updated DF with Extensions and Path:\n",df["image"][0])
  return df







from google.colab import drive
drive.mount('/content/drive')



########### Warmup Epochs is research paper implementations Research paper ######################
## below functions helpfull to preventions of exploding gradients problems
def cosine_decay_with_warmup(global_step,
                             learning_rate_base,
                             total_step,
                             warmup_learning_rate=0.0,
                             warmup_steps=0,
                             hold_base_rate_steps=0):
  ## in which learning rate grow linearly from warmup_learing rate
  """
  Arguments:
        global_step {int} -- global step.
        learning_rate_base {float} -- base learning rate.
        total_steps {int} -- total number of training steps.

    Keyword Arguments:
        warmup_learning_rate {float} -- initial learning rate for warm up. (default: {0.0})
        warmup_steps {int} -- number of warmup steps. (default: {0})
        hold_base_rate_steps {int} -- Optional number of steps to hold base learning rate
                                    before decaying. (default: {0})
    Returns:
      a float representing learning rate.

  """
  "Within the i-th run, we decay the learning rate with a cosine annealing for each batch as follows:"
  if total_step<warmup_steps:
    raise ValueError("Total_steps must be larger or eaqual to the warmup_steps... ")
  learning_rate=0.5* learning_rate_base*(1+np.cos(np.pi*(global_step-warmup_steps-hold_base_rate_steps)))

  if hold_base_rate_steps>0:
    learning_rate=np.where(global_step>warmup_steps+hold_base_rate_steps,learning_rate,learning_rate_base)

  if warmup_steps>0:
    if learning_rate_base<warmup_learning_rate:
      raise ValueError("Learning rate base must be larger or equal ot warmup_learning_rate::::")

  return np.where(global_step>total_step,0.0,learning_rate)

"""
        Constructor for cosine decay with warmup learning rate scheduler.

        Arguments:
        learning_rate_base {float} -- base learning rate.
        total_steps {int} -- total number of training steps.

        Keyword Arguments:
        global_step_init {int} -- initial global step, e.g. from previous checkpoint.
        warmup_learning_rate {float} -- initial learning rate for warm up. (default: {0.0})
        warmup_steps {int} -- number of warmup steps. (default: {0})
        hold_base_rate_steps {int} -- Optional number of steps to hold base learning rate
                                    before decaying. (default: {0})
        verbose {int} -- 0: quiet, 1: update messages. (default: {0})
        """
class WarmUpCosineDecayScheduler(keras.callbacks.Callback):
  def __init__(self,
               learning_rate_base,
               total_steps,
               global_step_init=0,
               warmup_learning_rate=0.0,
               warmup_steps=0,
               hold_base_rate_steps=0,
               verbose=0):

      super(WarmUpCosineDecayScheduler,self).__init__()
      self.learning_rate_base=learning_rate_base
      self.total_steps=total_steps
      self.warmup_learning_rate=warmup_learning_rate
      self.warmup_steps=warmup_steps
      self.hold_base_rate_steps=hold_base_rate_steps
      self.verbose=verbose
      self.learning_rates=[]

  def on_batch_end(self,batch,logs=None):
    self.global_step=self.global_step+1
    lr=k.get_value(self.model.optimizer.lr)### that takes optimal values as a backend
    self.learning_rates.append(lr)

  def on_batch_begin(self,batch,logs=None):
    lr= cosine_decay_with_warmup(global_step=self.global_step,
                                      learning_rate_base=self.learning_rate_base,
                                      total_steps=self.total_steps,
                                      warmup_learning_rate=self.warmup_learning_rate,
                                      warmup_steps=self.warmup_steps,
                                      hold_base_rate_steps=self.hold_base_rate_steps)

    k.set_value(self.model.optimizer.lr,lr)
    if self.verbose>0:
      print('\nBatch %05d: setting learning '
                  'rate to %s.' % (self.global_step + 1, lr))

def save_plot(history, save_dir):
    #  "Accuracy"
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    #plt.show()
    plt.savefig(save_dir + '_accuracy.jpg')
    plt.close()

    # "Loss"
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    #plt.show()
    plt.savefig(save_dir + '_loss.jpg')
    plt.close()

from tensorflow.keras.applications import EfficientNetB3, EfficientNetB4, EfficientNetB5, EfficientNetB6, EfficientNetB7
'''
# Expected Input shape for EfficientNet Model
    Base model	resolution
EfficientNetB0	224
EfficientNetB1	240
EfficientNetB2	260
EfficientNetB3	300
EfficientNetB4	380
EfficientNetB5	456
EfficientNetB6	528
EfficientNetB7	600
'''
# Initialise the Model Hyperparameter and training settings used to configure the model.
def model_parameter(selected_model):
    model_list = {
        "model2": {
            "backbone": EfficientNetB4,
            "target": 9,
            "resize": 380,
            "metadata": False,
            "initial_lr": 3e-5,
            "epochs": 15,
            'train_batch_size': 8,
            'validation_batch_size': 8,
            "savedModelByName": "Model2_EffB4_No_meta.h5",
            "saveFinalModelBy": "Model2",
            'log_by': "Model2_EffB4_No_meta.csv",
            'save_plot_name': 'Model2_EffB4_No_meta',
            'prediction_csv_name': 'Model2_EffB4_No_meta_prediction',
            'print_hyper_parameter': True,
            'input_image_size': 768,
            'print_trainable_layers': True,
            'print_model_summary': False,
            'visualise_augmented_data': False
        },
        "model10": {
            "backbone": EfficientNetB5,
            "target": 9,
            "resize": 448,
            "metadata": False,
            "initial_lr": 3e-5,
            "epochs": 15,
            'input_image_size': 512,
            'train_batch_size': 4,
            'validation_batch_size': 4,
            "savedModelByName": "Model10_EffB5_No_meta.h5",
            "saveFinalModelBy": "Model10",
            'log_by': "Model10_EffB5_No_meta.csv",
            'save_plot_name': 'Model10_EffB5_No_meta',
            'prediction_csv_name': 'Model10_EffB5_No_meta_prediction',
            'print_hyper_parameter': True,
            'print_trainable_layers': False,
            'print_model_summary': False,
            'visualise_augmented_data': False
        },
        "model12": {
            "backbone": EfficientNetB6,
            "target": 9,
            "resize": 528,
            "metadata": False,
            "initial_lr": 3e-5,
            "epochs": 15,
            'input_image_size': 768,
            'train_batch_size': 8,
            'validation_batch_size': 8,
            "savedModelByName": "Model12_EffB6_No_meta.h5",
            "saveFinalModelBy": "Model12",
            'log_by': "Model12_EffB6_No_meta.csv",
            'save_plot_name': 'Model12_EffB6_No_meta',
            'prediction_csv_name': 'Model12_EffB6_No_meta_prediction',
            'print_hyper_parameter': True,
            'print_trainable_layers': False,
            'print_model_summary': False,
            'visualise_augmented_data': False
        },
        "model16": {
            "backbone": EfficientNetB7,
            "target": 9,
            "resize": 380,
            "metadata": False,
            "initial_lr": 1e-5,
            "epochs": 15,
            'input_image_size': 768,
            'train_batch_size': 4,
            'validation_batch_size': 4,
            "savedModelByName": "Model16_EffB7_No_meta.h5",
            "saveFinalModelBy": "Model16",
            'log_by': "Model16_EffB7_No_meta.csv",
            'save_plot_name': 'Model16_EffB7_No_meta',
            'prediction_csv_name': 'Model16_EffB7_No_meta_prediction',
            'print_hyper_parameter': True,
            'print_trainable_layers': False,
            'print_model_summary': False,
            'visualise_augmented_data': False
        }
    }

    return model_list[selected_model]

"""#**Boomhhhh!! 🎇🎇 it is Training Time😣😣😣😣😣**"""

from tensorflow.keras.applications import EfficientNetB3, EfficientNetB4, EfficientNetB5, EfficientNetB6, EfficientNetB7
from tensorflow.keras import layers
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from tensorflow.python.keras.utils.data_utils import Sequence
from tensorflow.keras import backend as k
import albumentations as A
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
# tf.keras.layers.BatchNormalization

from keras.api._v2.keras import activations
def EffNet(input_size,num_classess,pretrained_model,
           lr_rate,print_trainable_layers=False,
           print_model_summary=False):## EfficientNet and used Transfer Learning
  base_model=pretrained_model(
      weights="imagenet",
      input_shape=input_size,
      include_top=False
  )

  def unfreeze_model(model,print_trainable,print_summary):## here we  used transfer learning
    for layer in model.layers[:]:
        if isinstance(layer, layers.BatchNormalization):
          layer.trainable = False

    ## print trainable layers summary
    if print_trainable:
      for layer in model.layers:
        print(layer,layer.trainable)## means how many training data train during model evaluations
    if print_summary:
      base_model.summary()

  ## unfreeze the model
  unfreeze_model(base_model,print_trainable_layers,print_model_summary)

  model=keras.Sequential()
  model.add(base_model)
  model.add(layers.Flatten(name="top_flatten"))
  model.add(layers.Dense(500,activation="relu",name="dense_500"))
  model.add(layers.Dense(256,activation="relu",name="dense_256"))
  model.add(layers.Dense(num_classess,activation="softmax",name="output_layer"))

  optimizer=Adam(learning_rate=lr_rate)
  model.compile(optimizer=optimizer,loss='categorical_crossentropy',metrics=["accuracy"])

  if print_model_summary:
    model.summary()
  return model

def train_model(model, train_generator, epoch, train_batch_size, validation_generator, validation_batch_size, train_step, valid_step,
callback):
    return model.fit(
      train_generator,
      epochs = epoch,
      batch_size = train_batch_size,
      validation_data = validation_generator,
      validation_batch_size = validation_batch_size,
      steps_per_epoch = train_step,
      validation_steps = valid_step,
      verbose = 1,
      callbacks = callback)

def augment_images(image_size):
    transforms_train = A.Compose([
        A.Transpose(p=0.5),
        A.VerticalFlip(p=0.5),
        A.HorizontalFlip(p=0.5),
        A.Rotate(p=0.5),
        A.RandomBrightness(limit=0.2, p=0.5),
        A.RandomContrast(limit=0.2, p=0.5),
        A.OneOf([
                A.MotionBlur(blur_limit=5),
                A.MedianBlur(blur_limit=5),
                A.GaussianBlur(blur_limit=5),
                A.GaussNoise(var_limit=(5.0, 30.0))
                ], p=0.7),
        A.OneOf([
                A.OpticalDistortion(distort_limit=1.0),
                A.GridDistortion(num_steps=5, distort_limit=1.),
                A.ElasticTransform(alpha=3)
                ], p=0.7),
        A.CLAHE(clip_limit=4.0, p=0.7),
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=10, p=0.5),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, border_mode=0, p=0.85),
        A.Resize(width=image_size, height=image_size),
        A.Cutout(max_h_size= int(image_size*0.375), max_w_size= int(image_size*0.375), num_holes=1, p=0.7),
        A.Normalize(),
    ])

    transforms_val = A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize()
    ])

    transforms_test = A.Compose([
        A.Resize(image_size, image_size),
        A.Normalize()
    ])

    return transforms_train, transforms_val, transforms_test

## Install ImageDataAugmentor
!pip install --upgrade albumentations -q
!pip install git+https://github.com/mjkvaak/ImageDataAugmentor -q

! pip install Keras-Preprocessing

from ImageDataAugmentor.image_data_augmentor import ImageDataAugmentor

from tensorflow.keras.preprocessing.image import ImageDataGenerator
import albumentations as A
def data_generator(seed, transforms_train, transforms_val, label,
train_path, image_resize, train_batch_size, validation_batch_size):

    train_datagen = ImageDataAugmentor(
        augment = transforms_train,
        preprocess_input = None,
        seed = seed,
        validation_split = 0.2) # Define validation split i.e 20% data is used for validation

    valid_datagen = ImageDataAugmentor(
            augment = transforms_val,
            preprocess_input = None,
            seed = seed,
            validation_split = 0.2) # Define validation split i.e 20% data is used for validation

    # Flow training images using train_datagen generator
    train_generator = train_datagen.flow_from_dataframe(
            dataframe = label,
            directory = train_path,
            x_col = 'image',
            y_col = 'diagnosis',
            target_size= image_resize,
            batch_size = train_batch_size,
            subset = 'training',
            class_mode='categorical',
            validate_filenames = False)

    validation_generator = valid_datagen.flow_from_dataframe(
            dataframe = label,
            directory = train_path,
            x_col = 'image',
            y_col = 'diagnosis',
            target_size= image_resize,
            batch_size = validation_batch_size,
            subset = 'validation',
            class_mode='categorical',
            validate_filenames = False)

    return train_generator, validation_generator



"""# **Loading Data and check our results**"""

# Load Libraries
from glob import glob
from functools import reduce
import os
import sys
import yaml
import shutil
from tqdm import tqdm
import pandas as pd
import pprint

from tensorflow.keras.applications import EfficientNetB3, EfficientNetB4, EfficientNetB5, EfficientNetB6, EfficientNetB7
from tensorflow.keras import layers
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, CSVLogger
from tensorflow.python.keras.utils.data_utils import Sequence
from tensorflow.keras import backend as K

import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
import numpy as np

import albumentations as A
from ImageDataAugmentor.image_data_augmentor import ImageDataAugmentor

model_config = 'model10'

# Get the model parameters
selected_model = model_parameter(model_config)

# # Define Model Log and Plot files
log_path = "./runs/"
os.makedirs(log_path, exist_ok = True)

plot_path = "./plot/"
os.makedirs(plot_path, exist_ok = True)

# ##################### Define path for Training and Testing Data #########################
train_path = "./{0}x{0}/".format(selected_model['input_image_size'])
test_path = "./{0}x{0}_test/".format(selected_model['input_image_size'])

save_model_path = "./saveModel/"
os.makedirs(save_model_path, exist_ok = True)

##################### Get Training and Testing Labels from Azure Instance
train_label = pd.read_csv("/content/drive/MyDrive/save_final_cancer_datasets/LoadedCSVFiles/train_2020_and_2019_with_9_Labels.csv")
test_label = pd.read_csv("/content/drive/MyDrive/save_final_cancer_datasets/LoadedCSVFiles/test_2020_no_PateintDetail.csv")

label = train_label
test_csv = test_label

# Append Image extension and file path to train and test CSV
absolute_path_train = os.path.abspath(train_path)
label =append_path(label, absolute_path_train)

absolute_path_test = os.path.abspath(test_path)
test_csv = append_path(test_csv, absolute_path_test)

##################### Hyper Parameter
hyper_param = {
    'seed': 42,
    'image_size': selected_model['resize'], # resize image
    'backbone_model': selected_model['backbone'], # Pretrained model name
    'early_stop': 10,
    'num_class': selected_model['target'],
    'train_batch_size': selected_model['train_batch_size'], # Train Batch Size
    'test_batch_size': 1, # Testing set batch size
    'validation_batch_size': selected_model['validation_batch_size'], # Validation Batch Size
    'epoch': selected_model['epochs'],
    'warmup_epoch': 1,
    'learning_rate_base': selected_model['initial_lr'], # Base learning rate after warmup.
    'warmup_learning_rate': selected_model['initial_lr'], # Warmup learning rate
    'training_sample_count': label.shape[0], # Number of training sample
    'save_model': selected_model['savedModelByName'], # save model name
    'save_final_model': selected_model['saveFinalModelBy'] # Save final trained model in Tensorflow Format
}

image_resize = (hyper_param['image_size'], hyper_param['image_size'])
image_shape = image_resize + (3, )
# Total training steps in Warmup
total_steps = int(hyper_param['epoch'] * hyper_param['training_sample_count'] / hyper_param['train_batch_size'])
# Compute the number of warmup batches.
warmup_steps = int(hyper_param['warmup_epoch'] * hyper_param['training_sample_count'] / hyper_param['train_batch_size'])

# Print Hyper parameter
if selected_model['print_hyper_parameter']:
    print("\n####################### Hyper Parameter #################################\n")
    pprint.pprint(hyper_param)

    print('\nImage Shape: {}'.format(image_shape))
    print('Total training steps in Warmup: {}'.format(total_steps))
    print('Number of Warmup Batch: {}\n'.format(warmup_steps))
    print("\nTrain Label shape: ", label.shape)
    print("Test Label shape: ", test_csv.shape)

########################### Train model
# Create the Learning rate scheduler.
warm_up_lr =WarmUpCosineDecayScheduler(learning_rate_base = hyper_param['learning_rate_base'],
                                        total_steps = total_steps,
                                        warmup_learning_rate = hyper_param['warmup_learning_rate'],
                                        warmup_steps = warmup_steps,
                                        hold_base_rate_steps = 0)

# Initialise Pre-train Model
model = EffNet(input_size = image_shape, num_classess = hyper_param['num_class'],
    pretrained_model = hyper_param['backbone_model'],
    lr_rate = hyper_param['learning_rate_base'],
    print_trainable_layers = selected_model['print_trainable_layers'],
    print_model_summary = selected_model['print_model_summary'])

# Preprocess and Augment Image for train, test and validation set.
transform_train, transform_val, transform_test =augment_images(hyper_param['image_size'])

# Prepare train, validation Generator
train_generator, validation_generator =data_generator(seed = hyper_param['seed'],
    transforms_train = transform_train, transforms_val = transform_val, label = label,
    train_path = train_path, image_resize = image_resize,  train_batch_size = selected_model['train_batch_size'],
    validation_batch_size = selected_model['validation_batch_size'])

print("###################Train Generator###############",train_generator)

# Visualise preprocess and augmented data
if selected_model['visualise_augmented_data']:
    # Get Train set
    train_generator.show_data()
    print(train_generator,"#######TrainGenrator data#########")
    # Get validation set
    validation_generator.show_data()

## Define Callbacks
# Define Early Stopping on validation loss
es = EarlyStopping(monitor='val_loss', mode = 'min', patience = hyper_param['early_stop'],\
    verbose = 1, restore_best_weights = True)

# Save model after each epoch
ck = ModelCheckpoint(save_model_path + hyper_param['save_model'], monitor='val_loss', \
    verbose = 1, save_best_only = False, save_weights_only= False, mode='auto')

# Save logs to CSV
# append=False -> overwrite existing file.
logs = CSVLogger(log_path + selected_model['log_by'], separator=",", append=False)

# Callback list
call_backs = [warm_up_lr, ck, logs]

# Get Train and validation step size
STEP_SIZE_TRAIN = train_generator.n//train_generator.batch_size
STEP_SIZE_VALID = validation_generator.n//validation_generator.batch_size

start_training = input("Do you want to start training the model? [y]es OR [n]o: ")
# Start the training process is the 'yes' input is received from the terminal

history =train_model(model = model, train_generator = train_generator, epoch = hyper_param['epoch'],
        train_batch_size = hyper_param['train_batch_size'], validation_generator = validation_generator,
        validation_batch_size = hyper_param['validation_batch_size'], train_step = STEP_SIZE_TRAIN,
        valid_step = STEP_SIZE_VALID, callback = call_backs)


# Plot Training and validation loss
print("\n------ Saving Training and Validation Plot --------")
# Training and validation: accuracy & loss
save_plot(history = history,save_dir = plot_path + selected_model['save_plot_name'])

############################ Predict on Testing Set
test_datagen = ImageDataAugmentor(augment = transform_test,preprocess_input = None,seed = hyper_param['seed'])

# Define test generator
test_generator = test_datagen.flow_from_dataframe(
    dataframe = test_csv,
    directory = test_path,
    x_col = 'image',
    target_size = image_resize,
    class_mode = None,
    batch_size = hyper_param['test_batch_size'],
    shuffle = False,
    validate_filenames = False)

# Get Test steps
STEP_SIZE_TEST = test_generator.n//test_generator.batch_size
test_generator.reset()

# predict on Testset
print("\n------ Predicting on Testset --------")
prediction = model.predict(test_generator, steps = STEP_SIZE_TEST, verbose = 1)
predicted_class_indices = np.argmax(prediction, axis=1)

# Map the predicted labels with their unique ids such as filenames.
labels = (train_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())
predictions = [labels[k] for k in predicted_class_indices]

# Save the prediction ot CSV File
filenames = test_generator.filenames
results = pd.DataFrame({"Filename":filenames,
                        "Predictions":predictions})

prediction_path = "./prediction/"
os.makedirs(prediction_path, exist_ok = True)

results.to_csv(prediction_path + selected_model['prediction_csv_name'] + ".csv", index=False)

##### Save Trained Model
print("\n ------------ Saving the Trained model ------------------------------------")
final_model_path = save_model_path + '{}/'.format(hyper_param['save_final_model'])
os.makedirs(final_model_path, exist_ok = True)

model.save(final_model_path, save_format="tf", include_optimizer = True)

print("""\n---------------------- Completed Model Training ---------------------------\n
------------------------- Stopping the Azure Instance ------------------------""")
# Stopping ComputeInstance will stop the billing meter and persist the state on the disk.
# Available Quota will not be changed with this operation.
# instance.stop(wait_for_completion=True, show_output=True)

def train_model(model, train_generator, epoch, train_batch_size, validation_generator, validation_batch_size, train_step, valid_step,
callback):
    return model.fit(
      train_generator,
      epochs = epoch,
      batch_size = train_batch_size,
      validation_data = validation_generator,
      validation_batch_size = validation_batch_size,
      steps_per_epoch = train_step,
      validation_steps = valid_step,
      verbose = 1,
      callbacks = callback)





















































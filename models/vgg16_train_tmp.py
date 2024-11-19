
########################################
# configuration
########################################

# Parallel CPU
NUM_PARALLEL_CALL = 15


#
#train=True
train=False

load_model=True
#load_model=False

#
#overwrite_train_model =True
overwrite_train_model=False

epoch = 10000
root_model = './models'
model_name = 'VGG16'
#dataset_name = 'CIFAR10'
dataset_name = 'ImageNet'

# dataset
#dataset_name='CIFAR-10'
#dataset_name='ImageNet'

#
root_tensorboard = './tensorboard/'

#
lmb = 1.0E-9

# data augmentation
# mixup
#en_mixup=True
en_mixup=False

# cutmix
en_cutmix=True
#en_cutmix=False

if dataset_name == 'ImageNet':
    num_class = 1000
elif dataset_name == 'CIFAR10':
    num_class = 10
else:
    assert False





import datetime
import shutil

import tensorflow as tf

import tensorflow_addons as tfa

from tensorflow.keras.applications.xception import Xception
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.resnet import ResNet50
from tensorflow.keras.applications.resnet import ResNet101
from tensorflow.keras.applications.resnet import ResNet152
from tensorflow.keras.applications.resnet_v2 import ResNet50V2
from tensorflow.keras.applications.resnet_v2 import ResNet101V2
from tensorflow.keras.applications.resnet_v2 import ResNet152V2
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.keras.applications.densenet import DenseNet121
from tensorflow.keras.applications.densenet import DenseNet169
from tensorflow.keras.applications.densenet import DenseNet201
from tensorflow.keras.applications.nasnet import NASNetMobile
from tensorflow.keras.applications.nasnet import NASNetLarge
from tensorflow.keras.applications.efficientnet import EfficientNetB0
from tensorflow.keras.applications.efficientnet import EfficientNetB1
from tensorflow.keras.applications.efficientnet import EfficientNetB2
from tensorflow.keras.applications.efficientnet import EfficientNetB3
from tensorflow.keras.applications.efficientnet import EfficientNetB4
from tensorflow.keras.applications.efficientnet import EfficientNetB5
from tensorflow.keras.applications.efficientnet import EfficientNetB6
from tensorflow.keras.applications.efficientnet import EfficientNetB7




from tensorflow.keras.preprocessing import image

from tensorflow.keras.applications.xception import preprocess_input as Xception_preprocess_input
from tensorflow.keras.applications.vgg16 import preprocess_input as VGG16_preprocess_input
from tensorflow.keras.applications.vgg19 import preprocess_input as VGG19_preprocess_input
from tensorflow.keras.applications.resnet import preprocess_input as ResNet_preprocess_input
from tensorflow.keras.applications.resnet_v2 import preprocess_input as ResNetV2_preprocess_input
from tensorflow.keras.applications.inception_v3 import preprocess_input as InceptionV3_preprocess_input
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input as InceptionResNetV2_preprocess_input
from tensorflow.keras.applications.mobilenet import preprocess_input as MobileNet_preprocess_input
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as  MobileNetV2_preprocess_input
from tensorflow.keras.applications.densenet import preprocess_input as DenseNet_preprocess_input
from tensorflow.keras.applications.nasnet import preprocess_input as NASNet_preprocess_input
from tensorflow.keras.applications.efficientnet import preprocess_input as EfficientNet_preprocess_input


from tensorflow.keras.applications import imagenet_utils

#from tensorflow.keras.preprocessing import img_to_array, load_img

#
import tensorflow_datasets as tfds
tfds.disable_progress_bar()

#
import tqdm

import os
import matplotlib as plt

import numpy as np
import argparse
import cv2


# snn library
import lib_snn

#
#tf.config.functions_run_eagerly()

#
gpu_number=0
os.environ["CUDA_VISIBLE_DEVICES"]=str(gpu_number)

global input_size
global input_size_pre_crop_ratio

#
#model_name='Xception'
model_name='VGG16'
#model_name='VGG19'
#model_name='ResNet50'
#model_name='ResNet101'
#model_name='ResNet152'
#model_name='ResNet50V2'
#model_name='ResNet101V2'
#model_name='ResNet152V2'
#model_name='InceptionV3'
#model_name='InceptionResNetV2'
#model_name='MobileNet'
#model_name='MobileNetV2'
#model_name='DenseNet121'
#model_name='DenseNet169'
#model_name='DenseNet201'
#model_name='NASNetMobile'
#model_name='NASNetLarge'
#model_name='EfficientNetB0'
#model_name='EfficientNetB1'
#model_name='EfficientNetB2'
#model_name='EfficientNetB3'
#model_name='EfficientNetB4'
#model_name='EfficientNetB5'
#model_name='EfficientNetB6'
#model_name='EfficientNetB7'

########
# cutmix
########
# mixup data augmentation
# from keras.io

def get_box(lambda_value):
    cut_rat = tf.math.sqrt(1.0-lambda_value)

    cut_w = input_size * cut_rat
    cut_w = tf.cast(cut_w, tf.int32)

    cut_h = input_size * cut_rat
    cut_h = tf.cast(cut_h, tf.int32)

    cut_x = tf.random.uniform((), minval=0, maxval=input_size, dtype=tf.int32)
    cut_y = tf.random.uniform((), minval=0, maxval=input_size, dtype=tf.int32)

    boundaryx1 = tf.clip_by_value(cut_x - cut_w//2, 0, input_size)
    boundaryy1 = tf.clip_by_value(cut_y - cut_h//2, 0, input_size)
    bbx2 = tf.clip_by_value(cut_x + cut_w//2, 0, input_size)
    bby2 = tf.clip_by_value(cut_y + cut_h//2, 0, input_size)

    target_h = bby2 - boundaryy1
    if target_h == 0:
        target_h += 1

    target_w = bbx2 - boundaryx1
    if target_w == 0:
        target_w += 1

    return boundaryx1, boundaryy1, target_w, target_h

#
def eager_cutmix(ds_one, ds_two, alpha=0.2):
    return tf.py_function(mixup, [ds_one, ds_two, alpha],[tf.float32,tf.float32])

#
def cutmix(train_ds_one, train_ds_two, alpha):
    (images_one, labels_one), (images_two, labels_two) = train_ds_one, train_ds_two

    # Get a sample from the Beta distribution
    batch_size = 1
    gamma_1_sample = tf.random.gamma(shape=(), alpha=alpha)
    gamma_2_sample = tf.random.gamma(shape=(), alpha=alpha)
    lambda_value = gamma_1_sample / (gamma_1_sample + gamma_2_sample)

    # Get the bounding box offsets, heights and widths
    boundaryx1, boundaryy1, target_w, target_h = get_box(lambda_value)

    images_one, labels_one = resize_with_crop_aug(images_one, labels_one)
    images_two, labels_two = resize_with_crop_aug(images_two, labels_two)

    # Get a patch from the second image
    crop2 = tf.image.crop_to_bounding_box(images_two, boundaryy1, boundaryx1, target_h, target_w)

    # Pad the images_two patch with the same offset
    images_two = tf.image.pad_to_bounding_box(crop2, boundaryy1, boundaryx1, input_size, input_size)

    # Get a patch from the first image
    crop1 = tf.image.crop_to_bounding_box(images_one, boundaryy1, boundaryx1, target_h, target_w)

    # Pad the images_one patch with the same offset
    img1 = tf.image.pad_to_bounding_box(crop1, boundaryy1, boundaryx1, input_size, input_size)

    # Modifi the first image by subtracting the patch
    images_one = images_one - img1

    # Add the modified images_one and images_two to get the CutMix image
    image = images_one + images_two

    # Adjust Lambda in accordanct to the pixel ration
    lambda_value = 1 - (target_w*target_h)/(input_size*input_size)
    lambda_value = tf.cast(lambda_value,tf.float32)

    # Combine the labels of both images
    label = lambda_value*labels_one + (1-lambda_value)*labels_two

    return (image, label)

########
# mixup
########
# mixup data augmentation
# from keras.io

def eager_mixup(ds_one, ds_two, alpha=0.2):
    return tf.py_function(mixup, [ds_one, ds_two, alpha],[tf.float32,tf.float32])
    #return tf.py_function(mixup, [ds_one, ds_two, alpha],[tf.uint8,tf.uint8,tf.int64),tf.float32])
    #return tf.py_function(mixup, [ds_one, ds_two, alpha],[(tf.uint8,tf.int64),(tf.uint8,tf.int64),tf.float32])

def mixup(ds_one, ds_two, alpha=0.2):

    # unpack two datasets
    images_one, labels_one = ds_one
    images_two, labels_two = ds_two
    batch_size = 1
    #batch_size = tf.shape(images_one)[0]
    #print(batch_size)
    #assert False

    #
    images_one, labels_one = resize_with_crop_aug(images_one, labels_one)
    images_two, labels_two = resize_with_crop_aug(images_two, labels_two)

    labels_one = tf.cast(labels_one,tf.float32)
    labels_two = tf.cast(labels_two,tf.float32)

    # sample lambda and reshape it to do the mixup
    gamma_1_sample = tf.random.gamma(shape=[batch_size], alpha=alpha)
    gamma_2_sample = tf.random.gamma(shape=[batch_size], alpha=alpha)
    l = gamma_1_sample / (gamma_1_sample+gamma_2_sample)
    #xx_l = l
    #x_l = tf.reshape(l, shape=(batch_size,1,1,1))
    #x_l = tf.broadcast_to(x_l, tf.shape(images_one))
    #y_l = tf.reshape(l, shape=(batch_size,1))
    #y_l = tf.broadcast_to(y_l, tf.shape(images_one))
    #y_l = l

    # perform mixup on both images and labels by combining a pair of images/labels
    # (one from each dataset) into one image/label
    #print(type(images_one[0]))
    ##print((images_one[0]))
    #assert False
    #images = tf.add(tf.multiply(images_one,x_l),tf.multiply(images_two,(1-x_l)))
    #images = tf.multiply(images_one,x_l)
    #$images = images_one * x_l
    #images = images_one * l
    images = images_one * l + images_two * (1-l)
    #images = x_l*images_one + (1-x_l)*labels_two
    #images=images_one
    labels = labels_one * l + labels_two * (1-l)
    #labels = labels_one * y_l
    #labels = labels_one * 0.2
    #labels = tf.add(tf.multiply())

    return (images,labels)

#
def eager_resize_with_crop(image, label):
    return tf.py_function(resize_with_crop,[image,label],[tf.float32, tf.int64])
    #return resize_with_crop(image,label)

#
#@tf.function
def resize_with_crop(image, label):
    #global input_size
    #global input_size_pre_crop

    i=image
    i=tf.cast(i,tf.float32)
    #i=tf.image.resize(i,256,preserve_aspect_ratio=True)

    #[w,h,c] = tf.shape(image)
    w=tf.shape(image)[0]
    h=tf.shape(image)[1]

    #s = 270 # 71.43. 90.06
    #s = 260 # 71.37, 90.09
    #s = 256 # 71.26, 90.10
    #s = 250 # 71.13, 90.05
    #print(tf.shape(image))
    #s = input_size_pre_crop
    s = input_size*input_size_pre_crop_ratio

    #if w >= h:
    if tf.greater(w,h):
        w = tf.cast(tf.math.multiply(tf.math.divide(w,h),s),tf.int32)
        ##i=tf.image.resize(i,(w,256),method='bicubic',preserve_aspect_ratio=True)
        #i=tf.image.resize(i,(w,256),method='bicubic')
        s=tf.cast(s,tf.int32)
        i=tf.image.resize(i,(w,s),method='lanczos3')
        #i=tf.image.resize(i,(w,s),method='lanczos5')
        #i=tf.image.resize(i,(w,s),method='bicubic')
    else:
        h = tf.cast(tf.math.multiply(tf.math.divide(h,w),s),tf.int32)
        ##i=tf.image.resize(i,(256,h),method='bicubic',preserve_aspect_ratio=True)
        #i=tf.image.resize(i,(256,h),method='bicubic')
        s=tf.cast(s,tf.int32)
        i=tf.image.resize(i,(s,h),method='lanczos3')
        #i=tf.image.resize(i,(s,h),method='lanczos5')
        #i=tf.image.resize(i,(s,h),method='bicubic')

    #i=tf.image.resize_with_crop_or_pad(i,224,224)
    i=tf.image.resize_with_crop_or_pad(i,input_size,input_size)
    #i=preprocess_input(i)

    #i = imagenet_utils.preprocess_input(i, mode='torch')
    i = imagenet_utils.preprocess_input(i, mode='caffe')

    #print(type(i))
    #print(i)
    #print(i.shape)
#
    #print(i,label)
    #print(type(i))
    #print(type(label))
#
    #print(tf.reduce_max(i))

    #
    label = tf.one_hot(label,num_class)

    return (i, label)


@tf.function
def gaussian_filter(input, filter_size):
    g_sigma = tf.random.uniform(shape=[],minval=0.1,maxval=2.0)
    filtered_image = tfa.image.gaussian_filter2d(image=input,
                                filter_shape=(filter_size,filter_size),
                                sigma=g_sigma,
                                )
    return filtered_image

#@tf.function
def resize_with_crop_aug(image, label):

    i=image
    i=tf.cast(i,tf.float32)
    #i=tf.image.resize(i,256,preserve_aspect_ratio=True)

    #[w,h,c] = tf.shape(image)
    w=tf.shape(image)[0]
    h=tf.shape(image)[1]

    #s = input_size
    s = input_size*input_size_pre_crop_ratio

    #if w >= h:
    if tf.greater(w,h):
        w = tf.cast(tf.math.multiply(tf.math.divide(w,h),s),tf.int32)
        ##i=tf.image.resize(i,(w,256),method='bicubic',preserve_aspect_ratio=True)
        #i=tf.image.resize(i,(w,256),method='bicubic')
        s=tf.cast(s,tf.int32)
        i=tf.image.resize(i,(w,s),method='lanczos3')
        #i=tf.image.resize(i,(w,s),method='lanczos5')
        #i=tf.image.resize(i,(w,s),method='bicubic')
    else:
        h = tf.cast(tf.math.multiply(tf.math.divide(h,w),s),tf.int32)
        ##i=tf.image.resize(i,(256,h),method='bicubic',preserve_aspect_ratio=True)
        #i=tf.image.resize(i,(256,h),method='bicubic')
        s=tf.cast(s,tf.int32)
        i=tf.image.resize(i,(s,h),method='lanczos3')
        #i=tf.image.resize(i,(s,h),method='lanczos5')
        #i=tf.image.resize(i,(s,h),method='bicubic')



    # data augmentation from "A Simple Framework for Contrastive Learning of Visual Representations"

    #i=tf.numpy_function(lambda i: tf.keras.preprocessing.image.random_zoom(i, (0.2,0.2)),[i],tf.float32)
    #i=tf.keras.preprocessing.image.random_zoom(i,[-0.1,0.2])
    #i=tf.keras.preprocessing.image.random_rotation(i,0.3)
    #i=tf.image.random_brightness(i,max_delta=63)
    #i=tf.image.random_contrast(i,lower=0.2,upper=1.8)

    # color jitter
    #i=tf.image.random_brightness(i,max_delta=0.8)
    i=tf.image.random_contrast(i,lower=0.2,upper=1.8)
    i=tf.image.random_brightness(i,max_delta=63)
    i=tf.image.random_saturation(i,lower=0.2,upper=1.8)
    i=tf.image.random_hue(i,0.2)
    #i=tf.clip_by_value(i,0,1)

    # random transformation
    #i=tf.image.resize_with_crop_or_pad(i,input_size,input_size)
    i=tf.image.random_crop(i,[input_size,input_size,3])
    i=tf.image.random_flip_left_right(i)

    # gaussian filter
    d_aug_g_filter=False
    if d_aug_g_filter:
        g_p = tf.random.uniform(shape=[],minval=0.0,maxval=1.0)
        g_filter_size = int(input_size*0.1)
        if tf.greater(g_p,0.5):
            g_sigma = tf.random.uniform(shape=[],minval=0.1,maxval=2.0)
            # for use sigma as a random value, we commented out lines of 262, 263 in filters.py
            # where gaussian_filter2d function is defined
            i = tfa.image.gaussian_filter2d(image=i,
                                    filter_shape=(g_filter_size,g_filter_size),
                                    sigma=g_sigma,
                                    )

    #
    i=preprocess_input(i)


    # one-hot vectorization - label
    label = tf.one_hot(label, num_class)

    return (i, label)



#def resize_with_crop_aug_cifar(image, label):


# models
models = {
    'Xception': Xception,
    'VGG16': VGG16,
    'VGG19': VGG19,
    'ResNet50': ResNet50,
    'ResNet101': ResNet101,
    'ResNet152': ResNet152,
    'ResNet50V2': ResNet50V2,
    'ResNet101V2': ResNet101V2,
    'ResNet152V2': ResNet152V2,
    'InceptionV3': InceptionV3,
    'InceptionResNetV2': InceptionResNetV2,
    'MobileNet': MobileNet,
    'MobileNetV2': MobileNetV2,
    'DenseNet121': DenseNet121,
    'DenseNet169': DenseNet169,
    'DenseNet201': DenseNet201,
    'NASNetMobile': NASNetMobile,
    'NASNetLarge': NASNetLarge,
    'EfficientNetB0': EfficientNetB0,
    'EfficientNetB1': EfficientNetB1,
    'EfficientNetB2': EfficientNetB2,
    'EfficientNetB3': EfficientNetB3,
    'EfficientNetB4': EfficientNetB4,
    'EfficientNetB5': EfficientNetB5,
    'EfficientNetB6': EfficientNetB6,
    'EfficientNetB7': EfficientNetB7,
}

preprocessor_input = {
    'Xception': Xception_preprocess_input,
    'VGG16': VGG16_preprocess_input,
    'VGG19': VGG19_preprocess_input,
    'ResNet50': ResNet_preprocess_input,
    'ResNet101': ResNet_preprocess_input,
    'ResNet152': ResNet_preprocess_input,
    'ResNet50V2': ResNetV2_preprocess_input,
    'ResNet101V2': ResNetV2_preprocess_input,
    'ResNet152V2': ResNetV2_preprocess_input,
    'InceptionV3': InceptionV3_preprocess_input,
    'InceptionResNetV2': InceptionResNetV2_preprocess_input,
    'MobileNet': MobileNet_preprocess_input,
    'MobileNetV2': MobileNetV2_preprocess_input,
    'DenseNet121': DenseNet_preprocess_input,
    'DenseNet169': DenseNet_preprocess_input,
    'DenseNet201': DenseNet_preprocess_input,
    'NASNetMobile': NASNet_preprocess_input,
    'NASNetLarge': NASNet_preprocess_input,
    'EfficientNetB0': EfficientNet_preprocess_input,
    'EfficientNetB1': EfficientNet_preprocess_input,
    'EfficientNetB2': EfficientNet_preprocess_input,
    'EfficientNetB3': EfficientNet_preprocess_input,
    'EfficientNetB4': EfficientNet_preprocess_input,
    'EfficientNetB5': EfficientNet_preprocess_input,
    'EfficientNetB6': EfficientNet_preprocess_input,
    'EfficientNetB7': EfficientNet_preprocess_input,
}

GPU = 'RTX_3090'
# NVIDIA TITAN V (12GB)
if GPU=='NVIDIA_TITAN_V':
    input_sizes = {
        'Xception': 299,
        'InceptionV3': 299,
        'InceptionResNetV2': 299,
        'NASNetLarge': 331,
        'EfficientNetB1': 240,
        'EfficientNetB2': 260,
        'EfficientNetB4': 380,
        'EfficientNetB5': 456,
        'EfficientNetB6': 528,
        'EfficientNetB7': 600,
    }

    batch_size_inference_sel ={
        'NASNetLarge': 128,
        'EfficientNetB4': 128,
        'EfficientNetB5': 128,
        'EfficientNetB6': 64,
        'EfficientNetB7': 64,
    }


input_sizes = {
    'Xception': 299,
    'InceptionV3': 299,
    'InceptionResNetV2': 299,
    'NASNetLarge': 331,
    'EfficientNetB1': 240,
    'EfficientNetB2': 260,
    'EfficientNetB4': 380,
    'EfficientNetB5': 456,
    'EfficientNetB6': 528,
    'EfficientNetB7': 600,
}

batch_size_inference_sel ={
    'NASNetLarge': 128,
    'EfficientNetB4': 128,
    'EfficientNetB5': 128,
    'EfficientNetB6': 64,
    'EfficientNetB7': 64,
}



batch_size_train_sel = {
    #'VGG16': 256,
    'VGG16': 512,
    #'VGG16': 1024,
    #'VGG16': 2048,
}



model = models[model_name]
preprocess_input = preprocessor_input[model_name]
input_size = input_sizes.get(model_name,224)
batch_size_inference = batch_size_inference_sel.get(model_name,256)
batch_size_train = batch_size_train_sel.get(model_name,256)



## ImageNet Dataset setup
if dataset_name == 'ImageNet':
    # Get ImageNet labels
    labels_path = tf.keras.utils.get_file('ImageNetwLabels.txt','https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt')
    imagenet_labels = np.array(open(labels_path).read().splitlines())

    print(imagenet_labels)

#    # Set data_dir to a read-only storage of .tar files
#    # Set write_dir to a w/r wtorage
    data_dir = '~/Datasets/ImageNet_down/'
    write_dir = '~/Datasets/ImageNet'
#
#    # Construct a tf.data.Dataset
    download_config = tfds.download.DownloadConfig(
        extract_dir=os.path.join(write_dir,'extracted'),
        manual_dir=data_dir
    )
#
    download_and_prepare_kwargs={
        'download_dir': os.path.join(write_dir, 'download'),
        'download_config': download_config
    }


    ds = tfds.load('imagenet2012',
                   data_dir=os.path.join(write_dir, 'data'),
                   split='validation',
                   #split=['train','validation']
                   shuffle_files=False,
                   download=True,
                   as_supervised=True,
                   #with_info=True,
                   download_and_prepare_kwargs=download_and_prepare_kwargs,
                   )


    input_size_pre_crop_ratio = 256/224
elif dataset_name == 'CIFAR10':
    #(train_ds, val_ds, test_ds) = tfds.load('cifar10',
    #                              split=['train[:90%]','train[90%:100%]','test'],
    #                              as_supervised=True,
    #                              batch_size=-1)

    f_cross_valid = False

    if f_cross_valid:
        train_ds = tfds.load('cifar10',
                             split=[f'train[:{k}%]+train[{k+10}%:]' for k in range(0,100,10)],
                             shuffle_files=True,
                             as_supervised=True)

        valid_ds = tfds.load('cifar10',
                             split=[f'train[{k}%:{k+10}%]' for k in range(0,100,10)],
                             shuffle_files=True,
                             as_supervised=True)

    elif en_mixup or en_cutmix:
        train_ds_1 = tfds.load('cifar10',
                             split='train',
                             shuffle_files=True,
                             as_supervised=True)

        train_ds_2 = tfds.load('cifar10',
                           split='train',
                           shuffle_files=True,
                           as_supervised=True)

        train_ds = tf.data.Dataset.zip((train_ds_1,train_ds_2))

        valid_ds = tfds.load('cifar10',
                            split='test',
                            as_supervised=True)
    else:
        train_ds, valid_ds = tfds.load('cifar10',
                             split=['train','test'],
                             shuffle_files=True,
                             as_supervised=True)

    test_ds = tfds.load('cifar10',
                      split='test',
                      as_supervised=True)

    #input_size_pre_crop_ratio = 36/32
    #input_size_pre_crop_ratio = 40/32
    #input_size_pre_crop_ratio = 128/112
    input_size_pre_crop_ratio = 256/224


else:
    assert False



#print(ds.batch_size)

#assert False

#assert isinstance(ds, tf.data.Dataset)


if dataset_name == 'ImageNet':
    include_top = True
else:
    # CIFAR-10
    #input_size=32
    input_size=224
    include_top = False

#
image_shape = (input_size, input_size, 3)

#
pretrained_model = model(input_shape=image_shape, include_top=include_top, weights='imagenet')
#pretrained_model = VGG16(include_top=True, weights='imagenet')
#pretrained_model = VGG19(include_top=True, weights='imagenet')
#pretrained_model = ResNet50(include_top=True, weights='imagenet')
#pretrained_model = ResNet101(include_top=True, weights='imagenet')

#pretrained_model.trainable = False







#
# only inference
if dataset_name == 'ImageNet':

    pretrained_model.compile(optimizer='adam',
                             loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                             #metrics=['accuracy'])
                             #metrics=[tf.keras.metrics.sparse_top_k_categorical_accuracy])
                             metrics=[tf.keras.metrics.categorical_accuracy, \
                                      tf.keras.metrics.top_k_categorical_accuracy])

    # Preprocess input
    #ds=ds.map(resize_with_crop,num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds=ds.map(resize_with_crop,num_parallel_calls=NUM_PARALLEL_CALL)
    #ds=ds.map(eager_resize_with_crop,num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds=ds.batch(batch_size_inference)
    #ds=ds.batch(250)
    #ds=ds.batch(2)
    #ds=ds.prefetch(tf.data.experimental.AUTOTUNE)
    ds=ds.prefetch(NUM_PARALLEL_CALL)


    #ds=ds.take(1)

    result = pretrained_model.evaluate(ds)
elif dataset_name == 'CIFAR10':

    # Preprocess input
    if train:
        if en_mixup:
            #train_ds_1=train_ds_1.map(resize_with_crop_aug,num_parallel_calls=tf.data.experimental.AUTOTUNE)
            #train_ds_1=train_ds_1.batch(batch_size_train)
            #train_ds_1=train_ds_1.prefetch(tf.data.experimental.AUTOTUNE)

            #train_ds_2=train_ds_2.map(resize_with_crop_aug,num_parallel_calls=tf.data.experimental.AUTOTUNE)
            #train_ds_2=train_ds_2.batch(batch_size_train)
            #train_ds_2=train_ds_2.prefetch(tf.data.experimental.AUTOTUNE)

            #train_ds=train_ds.map(lambda train_ds_1, train_ds_2: mixup(train_ds_1,train_ds_2,alpha=0.2),num_parallel_calls=tf.data.experimental.AUTOTUNE)
            train_ds=train_ds.map(lambda train_ds_1, train_ds_2: mixup(train_ds_1,train_ds_2,alpha=0.2),num_parallel_calls=NUM_PARALLEL_CALL)
            #train_ds=train_ds.map(lambda train_ds_1, train_ds_2: eager_mixup(train_ds_1,train_ds_2,alpha=0.2),num_parallel_calls=tf.data.experimental.AUTOTUNE)
            train_ds=train_ds.batch(batch_size_train)
            train_ds = train_ds.prefetch(NUM_PARALLEL_CALL)
        elif en_cutmix:
            train_ds = train_ds.map(lambda train_ds_1, train_ds_2: cutmix(train_ds_1, train_ds_2, alpha=0.2),
                                    num_parallel_calls=NUM_PARALLEL_CALL)
            #train_ds = train_ds.map(lambda train_ds_1, train_ds_2: eager_cutmix(train_ds_1, train_ds_2, alpha=0.2),
            #                        num_parallel_calls=NUM_PARALLEL_CALL)
            train_ds = train_ds.batch(batch_size_train)
            train_ds = train_ds.prefetch(NUM_PARALLEL_CALL)
        else:
            #train_ds=train_ds.map(resize_with_crop_aug,num_parallel_calls=tf.data.experimental.AUTOTUNE)
            train_ds=train_ds.map(resize_with_crop_aug,num_parallel_calls=NUM_PARALLEL_CALL)
            train_ds=train_ds.batch(batch_size_train)
            #train_ds=train_ds.prefetch(tf.data.experimental.AUTOTUNE)
            train_ds = train_ds.prefetch(NUM_PARALLEL_CALL)

    #valid_ds=valid_ds.map(resize_with_crop_cifar,num_parallel_calls=tf.data.experimental.AUTOTUNE)
    #valid_ds=valid_ds.map(resize_with_crop,num_parallel_calls=tf.data.experimental.AUTOTUNE)
    valid_ds=valid_ds.map(resize_with_crop,num_parallel_calls=NUM_PARALLEL_CALL)
    #valid_ds=valid_ds.batch(batch_size_inference)
    valid_ds=valid_ds.batch(batch_size_train)
    #valid_ds=valid_ds.prefetch(tf.data.experimental.AUTOTUNE)
    valid_ds=valid_ds.prefetch(NUM_PARALLEL_CALL)

    #test_ds=test_ds.map(resize_with_crop,num_parallel_calls=tf.data.experimental.AUTOTUNE)
    test_ds=test_ds.map(resize_with_crop,num_parallel_calls=NUM_PARALLEL_CALL)
    test_ds=test_ds.batch(batch_size_train)
    #test_ds=test_ds.prefetch(tf.data.experimental.AUTOTUNE)
    test_ds=test_ds.prefetch(NUM_PARALLEL_CALL)






    #feature = pretrained_model(train_ds)

    #
    #kernel_regularizer = tf.keras.regularizers.l2


    #
    pretrained_model.trainable=False
    model = tf.keras.Sequential()

    #train = True
    # data augmentation
    if train:
        #model.add(tf.keras.layers.GaussianNoise(0.1))
        model.add(tf.keras.layers.experimental.preprocessing.RandomZoom((-0.1,0.1)))
        model.add(tf.keras.layers.experimental.preprocessing.RandomRotation((-0.03,0.03)))

    model.add(pretrained_model)
    model.add(tf.keras.layers.Flatten(name='flatten'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(4096, activation='relu', kernel_regularizer=tf.keras.regularizers.L2(lmb), name='fc1'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(4096, activation='relu', kernel_regularizer=tf.keras.regularizers.L2(lmb), name='fc2'))
    #model.add(tf.keras.layers.Dense(1024, activation='relu', name='fc2'))
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(10, activation='softmax', name='predictions'))


    #x = pretrained_model(train_ds)
    #x = tf.keras.layers.Flatten(name='flatten')(x)
    #x = tf.keras.layers.Dense(4096, activation='relu', name='fc1')(x)
    #x = tf.keras.layers.Dense(4096, activation='relu', name='fc2')(x)
    #output = tf.keras.layers.Dense(10, activation='softmax', name='predictions')(x)



    #metric_accuracy = tf.keras.metrics.sparse_categorical_accuracy(name='accuracy')
    #metric_accuracy_top5 = tf.keras.metrics.sparse_top_k_categorical_accuracy(name='accuracy_top5')

    metric_accuracy = tf.keras.metrics.categorical_accuracy
    metric_accuracy_top5 = tf.keras.metrics.top_k_categorical_accuracy

    # TODO: move to configuration

    metric_name_acc='acc'
    metric_name_acc_top5='acc-5'
    monitor_cri = 'val_'+metric_name_acc

    metric_accuracy.name = metric_name_acc
    metric_accuracy_top5.name = metric_name_acc_top5

    model.compile(optimizer='adam',
                             loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                             #metrics=['accuracy'])
                             metrics=[metric_accuracy, metric_accuracy_top5])



    batch_size=batch_size_train

    exp_set_name = model_name+'_'+dataset_name
    #dir_model = './'+exp_set_name
    dir_model = os.path.join(root_model,exp_set_name)

    #file_name='checkpoint-epoch-{}-batch-{}.h5'.format(epoch,batch_size)
    #config_name='ep-{epoch:04d}_bat-{}_lmb-{:.1E}'.format(batch_size,lmb)
    #config_name='bat-{}_lmb-{:.1E}'.format(batch_size,lmb)
    if en_mixup:
        config_name='bat-{}_lmb-{:.1E}_mu'.format(batch_size,lmb)
    elif en_cutmix:
        config_name = 'bat-{}_lmb-{:.1E}_cm'.format(batch_size, lmb)
    else:
        config_name='bat-{}_lmb-{:.1E}'.format(batch_size,lmb)

    filepath = os.path.join(dir_model,config_name)



    ########################################
    #
    ########################################

    if load_model:
        # get latest saved model
        latest_model=lib_snn.util.get_latest_saved_model(filepath)
        load_path = os.path.join(filepath,latest_model)
        model = tf.keras.models.load_model(load_path)

        if not latest_model.startswith('ep-'):
            assert False, 'the dir name of latest model should start with ''ep-'''
        init_epoch = int(latest_model.split('-')[1])
    else:
        init_epoch = 0


    if train:
        print('Train mode')
        # remove dir - train model
        if not load_model:
            if overwrite_train_model:
                if os.path.isdir(filepath):
                    shutil.rmtree(filepath)

        #path_tensorboard = root_tensorboard+exp_set_name
        #path_tensorboard = root_tensorboard+filepath
        path_tensorboard = os.path.join(root_tensorboard,exp_set_name)
        path_tensorboard = os.path.join(path_tensorboard,config_name)

        if os.path.isdir(path_tensorboard):
            date_cur = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
            path_dest_tensorboard = path_tensorboard+'_'+date_cur
            print('tensorboard data already exists')
            print('move {} to {}'.format(path_tensorboard,path_dest_tensorboard))

            shutil.move(path_tensorboard,path_dest_tensorboard)

        #
        if load_model:
            print('Evaluate pretrained model')

            assert monitor_cri=='val_acc', 'currently only consider monitor criterion - val_acc'

            idx_monitor_cri = model.metrics_names.index('acc')

            result = model.evaluate(test_ds)

            best = result[idx_monitor_cri]

            print('previous best result - {}'.format(best))
        else:
            best = None

        #assert False
        #
        callbacks = [
            #tf.keras.callbacks.ModelCheckpoint(
            lib_snn.callbacks.ModelCheckpointResume(
                filepath=filepath+'/ep-{epoch:04d}',
                save_best_only=True,
                #monitor='val_acc',
                monitor=monitor_cri,
                #period=1,
                verbose=1,
                best=best
            ),
            tf.keras.callbacks.TensorBoard(log_dir=path_tensorboard,update_freq='epoch'),
            lib_snn.callbacks.ManageSavedModels(filepath=filepath)
        ]

        train_histories = model.fit(train_ds,epochs=epoch,initial_epoch=init_epoch,validation_data=valid_ds,callbacks=callbacks)
        #train_results = training_model.fit(train_ds,epochs=3,validation_data=valid_ds)

        #assert False

        #result = pretrained_model.evaluate(ds)
    else:
        print('Test mode')
        result = model.evaluate(test_ds)
        #result = model.predict(test_ds)

        print(result)


else:
    assert False

##result = pretrained_model.predict(ds)
#print(decode_predictions(result,top=1))
##print(dict(zip(pretrained_model.metrics_names, result)))
#print(zip(pretrained_model.metrics_names, result))
#print(pretrained_model.metrics)
#print(result)
#




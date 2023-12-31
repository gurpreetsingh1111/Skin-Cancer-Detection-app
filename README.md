# Skin-Cancer-Detection-app

## Abstract
In cancer, there are over 200 different forms. Out of 200, melanoma is the deadliest form of skin cancer. The diagnostic procedure for melanoma starts with clinical screening, followed by dermoscopic analysis and histopathological examination. Melanoma skin cancer is highly curable if it gets identified at the early stages. The first step of Melanoma skin cancer diagnosis is to conduct a visual examination of the skin's affected area. Dermatologists take the dermatoscopic images of the skin lesions by the high-speed camera, which have an accuracy of 65-80% in the melanoma diagnosis without any additional technical support. With further visual examination by cancer treatment specialists and dermatoscopic images, the overall prediction rate of melanoma diagnosis raised to 75-84% accuracy. The project aims to build an automated classification system based on image processing techniques to classify skin cancer using skin lesions images.

## Introduction and Background
Among all the skin cancer type, melanoma is the least common skin cancer, but it is responsible for **75% of death SIIM-ISIC Melanoma Classification, 2020**. Being a less common skin cancer type but is spread very quickly to other body parts if not diagnosed early. The International Skin Imaging Collaboration (ISIC) is facilitating skin images to reduce melanoma mortality. Melanoma can be cured if diagnosed and treated in the early stages. Digital skin lesion images can be used to make a teledermatology automated diagnosis system that can support clinical decision.

Currently, deep learning has revolutionised the future as it can solve complex problems. The motivation is to develop a solution that can help dermatologists better support their diagnostic accuracy by ensembling contextual images and patient-level information, reducing the variance of predictions from the model.

## The problem we tried to solve
The first step to identify whether the skin lesion is malignant or benign for a dermatologist is to do a skin biopsy. In the skin biopsy, the dermatologist takes some part of the skin lesion and examines it under the microscope. The current process takes almost a week or more, starting from getting a dermatologist appointment to getting a biopsy report. This project aims to shorten the current gap to just a couple of days by providing the predictive model using Computer-Aided Diagnosis (CAD). The approach uses Convolutional Neural Network (CNN) to classify nine types of skin cancer from outlier lesions images. This reduction of a gap has the opportunity to impact millions of people positively.

## Motivation
The overarching goal is to support the efforts to reduce the death caused by skin cancer. The primary motivation that drives the project is to use the advanced image classification technology for the well-being of the people. Computer vision has made good progress in machine learning and deep learning that are scalable across domains. With the help of this project, we want to reduce the gap between diagnosing and treatment. Successful completion of the project with higher precision on the dataset could better support the dermatological clinic work. The improved accuracy and efficiency of the model can aid to detect melanoma in the early stages and can help to reduce unnecessary biopsies.

## Application
We aim to make it accessible for everyone and leverage the existing model and improve the current system. To make it accessible to the public, we build an easy-to-use website. The user or dermatologist can upload the patient demographic information with the skin lesion image. With the image and patient demographic as input, the model will analyse the data and return the results within a split second. Keeping the broader demographic of people in the vision, we have also tried to develop the basic infographic page, which provides a generalised overview about melanoma and steps to use the online tool to get the results.



## Dataset
The project dataset is openly available on Kaggle (**SIIM-ISIC Melanoma Classification, 2020**). It consists of around forty-four thousand images from the same patient sampled over different weeks and stages. The dataset consists of images in various file format. The raw images are in DICOM (Digital Imaging and COmmunications in Medicine), containing patient metadata and skin lesion images. DICOM is a commonly used file format in medical imaging. Additionally, the dataset also includes images in TFRECORDS (TensorFlow Records) and JPEG format.

Furthermore, thirty-three thousand are in training set among the forty-four thousand images and around eleven thousand in the test set. However, our quick analysis found a significant class imbalance in the training dataset. Thirty-two thousand are labelled as benign (Not Cancerous) and only five hundred marked as malignant (Cancerous). That is, the training set contains only ±1.76% of malignant images (Figure 1). Along with the patient's images, the dataset also has a CSV file containing a detail about patient-level contextual information, which includes patient id, gender, patient age, location of benign/malignant site, and indicator of malignancy for the imaged lesion.

## Data Pre-Processing
In any machine learning project, it is critical to set up a trustworthy validation scheme, in order to properly evaluate and compare models. This is especially true if the dataset is small to medium size, or the evaluation metric is unstable, which is the case of this project.

There are 33k images in train data. However, only 1.76% are positive samples (i.e., malignant). The small number of positives causes the AUC metric to be very unstable, even with 5-fold cross validation.

Our solution to this problem is to use both last year (including 2018 and 2019) and this year's data (2020). Even though last year's data is smaller (25k), it has 10 times (17.85%) the positive sample ratio, making the metrices much more stable.

For a typical image classification problem, the standard approach is to take a deep CNN model (such as the most popular EffcientNet) trained on ImageNet, replace the last layer so that the output dimension equals the target's dimension, and fine tune it on the specific dataset.

The target to predict in this year's (2020) competition is binary-benign (i.e. no melanoma) or malignant (i.e. melanoma). We noticed that the target information is included in the diagnosis column: target is malignant if and only if diagnosis is melanoma. But diagnosis column is more granular when an image is benign. We believed using diagnosis as target to train the model could give the model more information.

The fact that diagnosis was the target to predict in last year's competition (including 2018 and 2019) makes this choice more logical. There is a small problem though. The set of diagnosis is different between this year and last year. We solved it by mapping this year's diagnosis to last year's according to the descriptions on last year's website. See Table 1 for the mapping. There are 9 target values in most of our models. In one model, we only used 4 target values (NV, MEL, BKL and Unknown) by mapping the other five (*) to Unknown.

## Data Augmentation
In a small size dataset, image augmentation is required to avoid overfitting the training dataset. After data aggregation, we have around 46k images in the training set. The dataset contains significant class imbalance, with most of the classes have an "Unknown" category (Table 2). We have defined our augmentation pipeline to deal with the class imbalance. The augmentation that helps to improve the prediction accuracy of the model is selected. The selected augmentation are as follows:

* **Transpose:** A spatial level transformation that transposes image by swapping rows and columns.
Flip: A spatial level transformation that flip image either/both horizontally and/or vertically. Images are randomly flipped either horizontally or vertically to make the model more robust.
 * **Rotate:** A spatial level transformation that randomly turns images for uniform distribution. Random rotation allows the model to become invariant to the object orientation.
* **RandomBrightness:** A pixel-level transformation that randomly changes the brightness of the image. As in real life, we do not have object under perfect lighting conditions and this augmentation help to mimic real-life scenarios.
* **RandomContrast:** A pixel-level transformation that randomly changes the contrast of the input image. As in real life, we do not have object under perfect lighting conditions and this augmentation help to mimic real-life scenarios.
* **MotionBlur:** A pixel-level transformation that applies motion blur using a random-sized kernel.
* **MedianBlur:** A pixel-level transformation that blurs input image using a median filter.
* **GaussianBlur:** A pixel-level transformation that blurs input image using a gaussian filter.
* **GaussNoise:** A pixel-level transformation that applies Gaussian noise to the image. This augmentation will simulate the measurement noise while taking the images
* **OpticalDistortion:** Optical distortion is also known as Lens error. It mimics the lens distortion effect.
* **GridDistortion:** An image warping technique driven by mapping between equivalent families of curves or edges arranged in a grid structure.
* **ElasticTransform:** A pixel-level transformation that divides the images into multiple grids and, based on edge displacement, the grid will be distorted. This transform helps the network to have a better understanding of edges while training.
* **CLAHE:** A pixel-level transformation that applies Contrast Limited Adaptive Histogram Equalization to the input image. This augmentation improves the contrast of the images.
* **HueSaturationValue:** A pixel-level transformation that randomly changes hue, saturation and value of the input image.
* **ShiftScaleRotate:** A spatial level transformation that randomly applies affine transforms: translate, scale and rotate the input. The allow scale and rotate the image by certain angles
* **Cutout:** A spatial level transformation that does a rectangular cut in the image. This transformation helps the network to focus on the different areas in the images.



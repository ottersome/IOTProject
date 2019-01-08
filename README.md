# Recipe API


## Introduction

This is the final project for the "Design and Implementation of IOT Applications" at 
National Chiao Tung University, Fall 2018 semseter.
For this project, the following libraries need to be installed:
-Flask
-Linebot API
-genderize
-clarifai
-DAN
-PIL
-requests

## Description

For this projecct, we decided to utilize a combination of the LineBot API, the Clarifai image
recognition library for Python, and simple database management to give our users the ability 
to get a recommendation for possible recipes using a simple image.

### How does it work?

The first step is adding our LineBot as a friend on the popular messaging app Line. When the program is run,
the bot will send a series of instructions, which reads:

> First send an image with the food item you want, then some questions follow to make your experience more
> customized.

There are several diffferent ways of interacting with the bot:

* sending **Allergies** or **Utensils**:This will make the bot send a list of allergies or utensils,
respectively.

* sending "These are my...": When the user sends this sentence, followed by "allergies" or "utensils", they
should also receive the values currently stored in their entry in our small database. 

* sending an image: The user can choose to send an image containing food items; using the Clarifai
library for Python we receive tags of items that might be contained within the picture. The tags are
then sent through IOTtalk to another script  and in turn to a recipe search engine. We then retrieve 
a page for a recipe containing the food/beverage items and then send them back to the user through 
LineBot.   

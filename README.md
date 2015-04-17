# Brglr

Brglr (because who needs vowels?) is an intruder detection application
 that will text an image of a potential intruder to your phone.

It was made for the Simpleweb hacknight sponsored by Twilio.

## Prerequisites

* `OpenCV`
* `twilio-python`
* `imgurpython`

## How?

Uses Collins et. al method for differential images, with a specified threshold. Then current frame is then taken and written to an image.

The image is uploaded to imgur and a link is attached to the body of the message sent using Twilio. Once MMS is available through Twilio in the UK it would be nice to use their `MediaUrl` property.

## Install
Assuming all prerequisties are installed.

`python brglr.py`

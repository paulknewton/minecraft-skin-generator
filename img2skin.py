# Create a Minecraft skin from a photo.
#
# usage: img2skin.py photo offsetX offsetY
#
# where:
#      photo: filename of the photo to process
#      offsetX: horixontal pixels to start extracting the skin
#      offsetY: vertical pixels to start extracting the skin
#
# Note: the shortest side of the input photo has 64 pixels, the longer side has more
#

from PIL import Image
import logging
import sys
import os
from mylib import *

logger = logging.getLogger('img2skin')
setupLogger(logger)
logger.setLevel(logging.DEBUG)

# skin dimensions
skinWidth = 64
skinHeight = 64

# These are the co-ordinates of the different body parts in a Minecraft skin and the corresponding
# position in a photo.
# The format of the dictionary is not the same as that used by the transformation functions,
# (topLeft/bottomRight co-ordinates are replaced by width/height and topLeft co-ordinates for example)
# but it is the format on the Minecraft Wiki page so is kept here unchanged.
#
# skin-topLeftX, skin-topLeftY, skin-bottomRightX, skin-bottomRightY, photo-topLeftX, photo-topLeftY
#
# (-1, -1) means the part cannot be found in a photo (so will need to be painted)
parts = {
    'headTop': [8, 0, 16, 8, 24, 0],
    'headBottom': [16, 0, 24, 8, -1, -1],
    'headRight': [0, 8, 8, 16, 16, 8],
    'headFront': [8, 8, 16, 16, 24, 8],
    'headLeft': [16, 8, 24, 16, 32, 8],
    'headBack': [24, 8, 32, 16, 8, 8],
    'rightLegTop': [4, 16, 8, 20, -1, -1],
    'rightLegBottom': [8, 16, 12, 20, -1, -1],
    'rightLegRight': [0, 20, 4, 32, 20, 28],
    'rightLegFront': [4, 20, 8, 32, 24, 28],
    'rightLegLeft': [8, 20, 12, 32, -1, -1],
    'rightLegBack': [12, 20, 16, 32, -1, -1],
    'torsoTop': [20, 16, 28, 20, -1, -1],
    'torsoBottom': [28, 16, 36, 20, -1, -1],
    'torsoRight': [16, 20, 20, 32, -1, -1],
    'torsoFront': [20, 20, 28, 32, 24, 16],
    'torsoLeft': [28, 20, 32, 32, -1, -1],
    'torsoBack': [32, 20, 40, 32, -1, -1],
    'rightArmTop': [44, 16, 48, 20, -1, -1],
    'rightArmBottom': [48, 16, 52, 20, -1, -1],
    'rightArmRight': [40, 20, 44, 32, 16, 16],
    'rightArmFront': [44, 20, 48, 32, 20, 16],
    'rightArmLeft': [48, 20, 52, 32, -1, -1],
    'rightArmBack': [52, 20, 56, 32, 12, 16],
    'leftLegTop': [20, 48, 24, 52, -1, -1],
    'leftLegBottom': [24, 48, 28, 52, -1, -1],
    'leftLegRight': [16, 52, 20, 64, -1, -1],
    'leftLegFront': [20, 52, 24, 64, 28, 28],
    'leftLegLeft': [24, 52, 28, 64, 32, 28],
    'leftLegBack': [28, 52, 32, 64, -1, -1],
    'leftArmTop': [36, 48, 40, 52, -1, -1],
    'leftArmBottom': [40, 48, 44, 52, -1, -1],
    'leftArmRight': [32, 52, 36, 64, -1, -1],
    'leftArmFront': [36, 52, 40, 64, 32, 16],
    'leftArmLeft': [40, 52, 44, 64, 36, 16],
    'leftArmBack': [44, 52, 48, 64, 40, 16]
}


def transformImage(imgWidth, imgHeight, background, mappings):
    """Create a new image based on the supplied mappings.

     Args:
         imgWidth: width of the new image
         imgHeight: height of the new image
         background: colour of new image (None is transparent)
         mappings: a dictionary of mappings of the form:
            key: [ sourceImage, widthToGrab, heightToGrab, fromTopLeftX, fromTopLeftY, toTopLeftX, toTopLeftY]
     Returns:
         the new image
     Raises:

     """
    newImg = Image.new('RGBA', (imgWidth, imgHeight), background)

    for part in mappings:
        logger.debug("Processing mapping: " + xstr(mappings[part]))
        srcImg, width, height, fromCoords, toCoords = mappings[part]
        fromX, fromY = fromCoords
        toX, toY = toCoords

        logger.debug("Slicing " + xstr(part) + " from (" + xstr(fromX) + ", " + xstr(
        fromY) + "),(" + xstr(fromX + width) + ", " + xstr(fromY + height) + ") to (" + xstr(toX) + ", " + xstr(toY) + ")")
        clipboard = srcImg.crop((fromX, fromY, fromX + width, fromY + height))
        newImg.paste(clipboard, (toX, toY, toX + width, toY + height))

    return newImg


def getPhotoCoords(partEntry):
    # -1, -1 in the final coords means it cannot be mapped to the photo
    if partEntry[4] == -1:
        return None
    else:
        # apply the offset values
        return (partEntry[4] + photoOffsetX, partEntry[5] + photoOffsetY)


def getSkinCoords(partEntry):
    return (partEntry[0], partEntry[1])


if __name__ == "__main__":

    # pass in command line arguments:
    #      photo: filename of the photo to process
    #      offsetX: horixontal pixels to start extracting the skin
    #      offsetY: vertical pixels to start extracting the skin
    if len(sys.argv) != 4:
        print("usage: img2skin.py photo offsetX offsetY")
        sys.exit()

    # setup the filenames
    photoFilename = sys.argv[1]
    photoBasename = os.path.splitext(photoFilename)[0]
    photoSuffix = os.path.splitext(photoFilename)[1]
    skinFilename = photoBasename + "-skin.png" # always use PNG (transparent)
    photoFilename2 = photoBasename + "2" + photoSuffix

    # used to shift the output in the target photo
    photoOffsetX = int(sys.argv[2])
    photoOffsetY = int(sys.argv[3])

    # open the reference images used to 'paint' body parts that are not available from the photo
    colours = {
        'lightGrey': Image.open('lightGrey.png'),
        'darkGrey': Image.open('darkGrey.png'),
        'blue': Image.open('blue.png'),
        'green': Image.open('green.png'),
        'black': Image.open('black.png')
    }

    logger.info("Converting photo '" + photoFilename + "' to skin '" + skinFilename + "'...")
    photo = Image.open(photoFilename)

    # resize the photo to match the skin size (keep the aspect ratio to avoid stretching)
    logger.debug("Resizing the photo from " + xstr(photo.width) + "x" + xstr(photo.height) + " to " + xstr(skinWidth) + "x" + xstr(skinHeight))
    widthScale = photo.width / skinWidth
    heightScale = photo.height / skinHeight
    photoScale = min(widthScale, heightScale)
    logger.debug("Scaling factor = " + xstr(photoScale))
    photo = photo.resize((photo.width / photoScale, photo.height / photoScale))

    # Build the mappings to build the skin from the photo
    # by reading the position of each body part in the photo, and finding the location
    # in the Minecraft skin format.
    # If the part does not need to be taken from the photo,
    # use one of the reference images to 'paint' the part instead.
    # The image where the pixels are to be taken from are included in each
    # mapping entry (it is not always the photo - it is sometimes one of the reference images)
    mappingPhotoToSkin = {}
    for part in parts:
        fromCoords = getPhotoCoords(parts[part])
        if fromCoords is None:
            # cannot use photo, so need to select another colour
            #colour = 'lightGrey'    # default (e.g. back)
            colour = 'green'
            if 'Leg' in xstr(part):
                colour = 'blue'
            if 'Arm' in xstr(part):
                colour = 'green'
            if 'Bottom' in xstr(part):  # takes priority over leg/arm
                colour = 'darkGrey'
            logger.debug("Painting " + xstr(part) + " with " + xstr(colour) + " because fromCoords are None")
            fromImg = colours[colour] # uncomment this if you want textures
            #fromImg = colours['black'] # uncomment this if you want black
            fromCoords = (0,0)

        else:
            fromCoords = (fromCoords[0] + photoOffsetX, fromCoords[1] + photoOffsetY)
            fromImg = photo

        toCoords = getSkinCoords(parts[part])
        mappingPhotoToSkin[xstr(part)] = [fromImg, parts[part][2] - parts[part][0], parts[part][3] - parts[part][1], fromCoords, toCoords]
        logger.debug("Adding " + xstr(part) + ": " + xstr(mappingPhotoToSkin[xstr(part)]))

    # create the skin
    skin = transformImage(64, 64, None, mappingPhotoToSkin)
    skin.save(skinFilename)
    photo.close()

    # Now build a photo of the skin by applying the transformation with the mappings/source image reversed.
    # This is useful to visualise how the skin will look when uploaded to Minecraft.
    # The photo is the skin unwrapped (e.g. head top unfolds at the top, back arms on the left/right etc).
    logger.info("Converting skin '" + skinFilename + "' back to photo '" + photoFilename2 + "'")
    mappingSkinToPhoto = {}
    for part in parts:
        toCoords = getPhotoCoords(parts[part])
        if toCoords is None:
            # if the body part doesn't appear on the photo, just skip it (no need to 'paint it' as before
            logger.debug("Skipping " + xstr(part) + " because toCoords are None")
            continue

        fromCoords = getSkinCoords(parts[part])
        mappingSkinToPhoto[xstr(part)] = [skin, parts[part][2] - parts[part][0], parts[part][3] - parts[part][1], fromCoords, toCoords]
        logger.debug("Adding " + xstr(part) + ": " + xstr(mappingSkinToPhoto[xstr(part)]))

    photo = transformImage(skin.width, skin.height, 'white', mappingSkinToPhoto)
    photo.save(photoBasename + '2' + '.png')



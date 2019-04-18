"""usage: photo2skin.py [-h] photo_filename offset_x offset_y

Create a Minecraft skin from a photo.

positional arguments:
  photo_filename  filename of the photo to process
  offset_x        horizontal offset in photo
  offset_y        vertical offset in photo

optional arguments:
  -h, --help      show this help message and exit"""

import argparse
import os

from PIL import Image

from mylib import *

logger = logging.getLogger('photo2skin')
setupLogger(logger)
logger.setLevel(logging.INFO)

# skin dimensions
SKIN_WIDTH = 64
SKIN_HEIGHT = 64

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


def transform_image(new_width, new_height, background, mappings):
    """Create a new image based on the supplied mappings. Helper function to build images photo > skin > thumbnail

     Args:
         new_width: width of the new image
         new_height: height of the new image
         background: colour of new image (None is transparent)
         mappings: a dictionary of mappings of the form:
            key: [ sourceImage, widthToGrab, heightToGrab, fromTopLeftX, fromTopLeftY, toTopLeftX, toTopLeftY]
     Returns:
         the new image
     Raises:

     """
    new_img = Image.new('RGBA', (new_width, new_height), background)

    for part in mappings:
        logger.debug("Processing mapping: " + xstr(mappings[part]))
        src_img, width, height, (from_x, from_y), (to_x, to_y) = mappings[part]

        logger.debug("Slicing " + xstr(part) + " from (" + xstr(from_x) + ", " + xstr(
            from_y) + "),(" + xstr(from_x + width) + ", " + xstr(from_y + height) + ") to (" + xstr(to_x) + ", " + xstr(
            to_y) + ")")
        clipboard = src_img.crop((from_x, from_y, from_x + width, from_y + height))
        new_img.paste(clipboard, (to_x, to_y, to_x + width, to_y + height))

    return new_img


def get_photo_coords(part_entry, photo_offset_x, photo_offset_y):
    """Get the matching co-ordinates in the photo for a given body part.

    Args:
        part_entry - the entry for a body part of the form [skin-topLeftX, skin-topLeftY, skin-bottomRightX, skin-bottomRightY, photo-topLeftX, photo-topLeftY]
        photo_offset_x - horizontal offset to shift the photo
        photo_offset_y - vertical offset to shift the photo
    Returns:
        tuple of x,y co-ordinates
    """
    # -1, -1 in the final coords means it cannot be mapped to the photo
    if part_entry[4] == -1:
        return None
    else:
        # apply the offset values
        return (part_entry[4] + photo_offset_x, part_entry[5] + photo_offset_y)


def get_skin_coords(part_entry):
    """Get the matching co-ordinates in the photo for a given body part.

    Args:
        part_entry - the entry for a body part of the form [skin-topLeftX, skin-topLeftY, skin-bottomRightX, skin-bottomRightY, photo-topLeftX, photo-topLeftY]
    """
    return (part_entry[0], part_entry[1])


def build_skin(photo_filename, photo_offset_x, photo_offset_y):
    """Build a minecraft skin and a thumbnail from the provided photo image."""

    # open the reference images used to 'paint' body parts that are not available from the photo
    colours = {
        'lightGrey': Image.open('lightGrey.png'),
        'darkGrey': Image.open('darkGrey.png'),
        'blue': Image.open('blue.png'),
        'green': Image.open('green.png'),
        'black': Image.open('black.png')
    }

    logger.info("Converting photo '" + photo_filename + "' to skin with offset (%d, %d)" % (photo_offset_x, photo_offset_y))
    photo = Image.open(photo_filename)

    # resize the photo to match the skin size (keep the aspect ratio to avoid stretching)
    photoScale = min(photo.width / SKIN_WIDTH, photo.height / SKIN_HEIGHT)
    logger.debug("Scaling factor = " + xstr(photoScale))

    x = int(photo.width / photoScale)
    y = int(photo.height / photoScale)
    logger.info("Resizing the photo from %dx%d to %dx%d" % (photo.width, photo.height, x, y))
    photo = photo.resize((x, y))

    # Build the mappings to build the skin from the photo
    # by reading the position of each body part in the photo, and finding the location
    # in the Minecraft skin format.
    # If the part does not need to be taken from the photo,
    # use one of the reference images to 'paint' the part instead.
    # The image where the pixels are to be taken from are included in each
    # mapping entry (it is not always the photo - it is sometimes one of the reference images)
    mapping_photo_to_skin = {}
    for part in parts:
        from_coords = get_photo_coords(parts[part], photo_offset_x, photo_offset_y)
        if from_coords is None:
            # cannot use photo, so need to select another colour
            # colour = 'lightGrey'    # default (e.g. back)
            colour = 'green'
            if 'Leg' in xstr(part):
                colour = 'blue'
            if 'Arm' in xstr(part):
                colour = 'green'
            if 'Bottom' in xstr(part):  # takes priority over leg/arm
                colour = 'darkGrey'
            logger.debug("Painting " + xstr(part) + " with " + xstr(colour) + " because from_coords are None")
            from_img = colours[colour]  # uncomment this if you want textures
            # from_img = colours['black'] # uncomment this if you want black
            from_coords = (0, 0)

        else:
            from_coords = (from_coords[0] + photo_offset_x, from_coords[1] + photo_offset_y)
            from_img = photo

        to_coords = get_skin_coords(parts[part])
        mapping_photo_to_skin[xstr(part)] = [from_img, parts[part][2] - parts[part][0], parts[part][3] - parts[part][1],
                                             from_coords, to_coords]
        logger.debug("Adding " + xstr(part) + ": " + xstr(mapping_photo_to_skin[xstr(part)]))

    # create the skin
    skin = transform_image(64, 64, None, mapping_photo_to_skin)
    photo.close()

    return skin


def build_thumbnail(skin, photo_offset_x, photo_offset_y):
    # Now build a photo of the skin by applying the transformation with the mappings/source image reversed.
    # This is useful to visualise how the skin will look when uploaded to Minecraft.
    # The photo is the skin unwrapped (e.g. head top unfolds at the top, back arms on the left/right etc).
    logger.info("Converting skin back to photo...")
    mapping_skin_to_photo = {}
    for part in parts:
        to_coords = get_photo_coords(parts[part], photo_offset_x, photo_offset_y)
        if to_coords is None:
            # if the body part doesn't appear on the photo, just skip it (no need to 'paint it' as before
            logger.debug("Skipping " + xstr(part) + " because to_coords are None")
            continue

        from_coords = get_skin_coords(parts[part])
        mapping_skin_to_photo[xstr(part)] = [skin, parts[part][2] - parts[part][0], parts[part][3] - parts[part][1],
                                             from_coords, to_coords]
        logger.debug("Adding " + xstr(part) + ": " + xstr(mapping_skin_to_photo[xstr(part)]))

    photo = transform_image(skin.width, skin.height, 'white', mapping_skin_to_photo)

    return photo


if __name__ == "__main__":

    # read command-line args
    parser = argparse.ArgumentParser(description="Create a Minecraft skin from a photo.")
    parser.add_argument("photo_filename", help="filename of the photo to process")
    parser.add_argument("-x", dest="offset_x", help="horizontal offset in photo", type=int, default=0)
    parser.add_argument("-y", dest="offset_y", help="vertical offset in photo", type=int, default=0)
    args = parser.parse_args()
    print(args)

    photo_filename = args.photo_filename
    photo_basename = os.path.splitext(photo_filename)[0]
    photo_suffix = os.path.splitext(photo_filename)[1]

    skin = build_skin(photo_filename, args.offset_x, args.offset_y)
    skin_filename = photo_basename + "-skin.png"
    logger.info("Saving skin as %s" % skin_filename)
    skin.save(skin_filename)  # always use PNG (transparent)

    thumbnail = build_thumbnail(skin, args.offset_x, args.offset_y)
    thumb_filename = photo_basename + "-thumb.png"
    logger.info("Saving thumbnail as %s" % thumb_filename)
    thumbnail.save(thumb_filename)

#!/usr/bin/env python

#   Gimp-Python - allows the writing of Gimp plugins in Python.
#   Copyright (C) 2015  William Bell <william.bell@frog.za.net>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gimpfu import *
import time
from array import array

gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

def column_flip(img, layer, col_number):
    gimp.progress_init("Processing" + layer.name + "...")
    pdb.gimp_undo_push_group_start(img)

    layername = "flipped " + layer.name

    # Create the new layer:
    srcWidth, srcHeight = layer.width, layer.height
    col_width = int(srcWidth / col_number)
    col_mid = int(col_width / 2)

    destDrawable = gimp.Layer(img, layername, srcWidth, srcHeight,
                              layer.type, layer.opacity, layer.mode)
    img.add_layer(destDrawable, 0)
    xoff, yoff = layer.offsets

    destDrawable.translate(xoff, yoff)

    srcRgn = layer.get_pixel_rgn(0, 0, srcWidth, srcHeight, False, False)
    src_pixels = array("B", srcRgn[0:srcWidth, 0:srcHeight])

    dstRgn = destDrawable.get_pixel_rgn(0, 0, srcWidth, srcHeight, True, True)
    p_size = len(srcRgn[0,0])
    dest_pixels = array("B", [0] * (srcWidth * srcHeight * p_size))

    # Finally, loop over the region:
    for c in xrange(0, int(col_number)) :
        for x in xrange(0, col_mid) :
            for y in xrange(0, srcHeight) :
                val1_pos = (c * col_width + x + srcWidth * y) * p_size
                val2_pos = (c * col_width + col_width - x - 1 + srcWidth * y) * p_size

                val1 = src_pixels[val1_pos: val1_pos + p_size]
                val2 = src_pixels[val2_pos: val2_pos + p_size]

                dest_pixels[val1_pos : val1_pos + p_size] = val2
                dest_pixels[val2_pos : val2_pos + p_size] = val1

        progress = float(x)/layer.width
        if (int(progress * 100) % 200 == 0) :
            gimp.progress_update(progress)

    # Copy the whole array back to the pixel region:
    dstRgn[0:srcWidth, 0:srcHeight] = dest_pixels.tostring()

    destDrawable.flush()
    destDrawable.merge_shadow(True)
    destDrawable.update(0, 0, srcWidth,srcHeight)

    # Remove the old layer
    #img.remove_layer(layer)
    layer.visible = False

    pdb.gimp_selection_none(img)
    pdb.gimp_image_undo_group_end(img)


register(
    "python-fu-column_flip",
    N_("Divides an image into columns and flips them."),
    "Adds a new layer to the image",
    "William Bell",
    "William Bell",
    "2015",
    N_("Flip _Columns..."),
    "RGB*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_SPINNER, "col_number",    _("Number of Columns:"),  5, (1, 256, 1)),
    ],
    [],
    column_flip,
    menu="<Image>/Image/Transform",
    domain=("gimp20-python", gimp.locale_directory)
    )

main()

from PIL import Image


# Get the layers, and voxel dims
numLayers = input("Enter the number of layers: ")
xVoxelDim = float(input("Enter the Voxel Dimension in the X axis: "))
yVoxelDim = float(input("Enter the Voxel Dimension in the Y axis: "))

# Create the G-Code file to write to
file = open("output.gcode", "w")

# Write Starting G-Code
line = "G91\n"
file.write(line)

# Load in the base layer to find the pixel dimensions
image = Image.open('0.bmp')
xPx, yPx = image.size

# For each layer
for layer in range(int(numLayers)):
    # Load the file
    filename = str(layer) + ".bmp"
    image = Image.open(filename)
    # For each row
    for y in range(yPx):

        # Clear out some line tracking variables
        segmentCount = int(0)
        rate, previousExtrude, unused = image.getpixel((0, yPx - y - 1))
        # For each pixel
        for x in range (xPx):
            # Extract the colors of the pixel
            rate, extrude, unused = image.getpixel((x, yPx - y - 1))

            # Check if our extrude value has changed for this voxel
            if extrude != previousExtrude:
                # If we're here, we're starting a new segment

                # First we need to write the line that just ended
                line = "G1 X" + str(segmentCount * xVoxelDim) + " Y0 E" + str((255-previousExtrude)/255 * xVoxelDim *
                                                                              segmentCount) + "\n"
                file.write(line)

                # Now reset the segment count for a new line
                segmentCount = 1
            else:
                segmentCount += 1

            # Update Previous Extrusion Value
            previousExtrude = extrude

        # Write the last remaining segment
        line = "G1 X" + str(int(segmentCount * xVoxelDim)) + " Y0 E" + str((255-previousExtrude)/255 * xVoxelDim *
                                                                           segmentCount) + "\n"
        file.write(line)

        # And Move to the next Line unless it was the last line
        if y < yPx - 1:
            line = "G1 Y" + str(yVoxelDim * 2) + "\n" +\
                   "G1 X-" + str(xPx * xVoxelDim) + "\n" +\
                   "G1 Y-" + str(yVoxelDim) + "\n"
            file.write(line)

file.close()

from PIL import Image


def print_move_line(X, Y, Z, F, E):
    line = "G1 X" + str(X) + " Y" + str(Y) + " Z" + str(Z) + " F" + str(F) + " E" + str(E)
    print_line(line)


def print_line(line):
    file.write(line + "\n")


# Get the layers, and voxel dims
numLayers = input("Enter the number of layers: ")
xVoxelDim = float(input("Enter the Voxel Dimension in the X axis: "))
yVoxelDim = float(input("Enter the Voxel Dimension in the Y axis: "))

# Declare some constants (for now)
zVoxelDim = float(0.5)
fMax = float(300)
eMax = float(1.5)

# Open the file to start writing
file = open("output.gcode", "w")

# Write Starting G-Code
print_line("G91")

# Load in the base layer to find the pixel dimensions
image = Image.open('0.bmp')
xPx, yPx = image.size
xCurrent = -1
yCurrent = -1
zCurrent = -1

# For each layer
for layer in range(int(numLayers)):
    # Load the file
    filename = str(layer) + ".bmp"
    image = Image.open(filename)
    # For each row
    for y in range(yPx):

        # Clear out some line tracking variables (Reading rows backwards)
        segmentCount = int(0)
        previousRate, previousExtrude, previousUnused = image.getpixel((0, yPx - y - 1))

        # Scale previousRate and previousExtrude to actual units
        previousRate = (255 - previousRate) * fMax / 255
        previousExtrude = (255 - previousExtrude) * eMax / 255

        # For each pixel
        for x in range(xPx):
            # Extract the colors of the pixel (Read rows backwards)
            rate, extrude, unused = image.getpixel((x, yPx - y - 1))

            # Scale previousRate and previousExtrude to actual units
            rate = (255 - rate) * fMax / 255
            extrude = (255 - extrude) * eMax / 255

            # Check to see if this is the start of the print
            if rate != 0 and xCurrent == -1:
                xCurrent = x
                yCurrent = y
                zCurrent = layer
                print_move_line(xCurrent * xVoxelDim, yCurrent * yVoxelDim, layer * zVoxelDim, fMax, 0)

                # Turn on the Welder

                # Record Previous Rates, Extrusions, and unused
                previousRate = rate
                previousExtrude = extrude
                previousUnused = unused
            # Now check if it's a new layer
            elif rate != 0 and layer != zCurrent:
                xTravel = (x - xCurrent) * xVoxelDim
                yTravel = (y - yCurrent) * yVoxelDim
                zTravel = (layer - zCurrent) * zVoxelDim
                print_move_line(xTravel, yTravel, zTravel, fMax, 0)
                xCurrent = x
                yCurrent = y
                zCurrent = layer
            # Otherwise, check if this is a new row
            elif rate != 0 and y != yCurrent:
                xTravel = (x - xCurrent) * xVoxelDim
                yTravel = (y - yCurrent) * yVoxelDim
                print_move_line(xTravel, yTravel, 0, fMax, 0)
                xCurrent = x
                yCurrent = y
                zCurrent = layer

                # Record Previous Rates, Extrusions, and unused
                previousRate = rate
                previousExtrude = extrude
                previousUnused = unused

            # Once one of the variables has changed, we're on a new segment
            if rate != previousRate or extrude != previousExtrude or unused != previousUnused:
                # Create the new line
                xTravel = (x - xCurrent) * xVoxelDim
                eTravel = xTravel * previousExtrude
                print_move_line(xTravel, 0, 0, previousRate, eTravel)
                xCurrent = x
                yCurrent = y
                zCurrent = layer

                # Record Previous Rates, Extrusions, and unused
                previousRate = rate
                previousExtrude = extrude
                previousUnused = unused

            # Detect if we're at the edge of the row
            if x == xPx - 1:
                # If there was no rate, we do nothing
                # If there was rate
                if rate != 0:
                    xTravel = (x - xCurrent + 1) * xVoxelDim
                    eTravel = xTravel * previousExtrude
                    print_move_line(xTravel, 0, 0, previousRate, eTravel)
                    xCurrent = x + 1
                    yCurrent = y
                    zCurrent = layer


# Close the file we wrote to
file.close()

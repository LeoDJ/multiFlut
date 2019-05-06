from PIL import Image
import time

def generatePFLines(img, offX = 0, offY = 0, algo=0):
    if img.format == "PNG":
        img = img.convert('RGBA')
        pfPixels = []
        if algo == 0:
            img_arr = img.load()
            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    rgb = img_arr[x, y]  # takes about 0.135us
                    if rgb[3] > 0:  # ignore transparent pixels, takes about 1.29us
                        hexColor = '%02x%02x%02x%02x' % rgb
                        pfPixels.append('PX %d %d %s\n' % (x + offX, y + offY, hexColor))
                    # print(x, y, rgb)
        return pfPixels
    else:
        return []

def main():
    t = time.time()
    img = Image.open('../noise.png')
    for i in range(1):
        print(len(generatePFLines(img)))
    print(time.time() - t)

if __name__ == "__main__":
    main()

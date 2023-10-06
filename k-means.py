import sys;args = sys.argv[1:]
from PIL import Image
# Nicholas Bonanno, pd. 6
import math
import time
def main():
    global args, pixels
    DEBUG = False
    if not args:
        DEBUG = False
        args = ['10', 'C:/bird_small.png']
    start = time.time()
    k_count = int(args[0])
    img = Image.open(args[1]).convert('RGB')
    load = img.load()

    print(f'Size: {img.width} x {img.height}')
    print(f'Pixels: {img.width * img.height}')
    pixels = list(img.getdata())
    distinct_pixels = dict()
    for pixel in pixels:
        if pixel not in distinct_pixels:
            distinct_pixels[pixel] = 0
        distinct_pixels[pixel] += 1
    print(f'Distinct pixel count: {len(distinct_pixels)}')
    greatest_count = (0, None)
    for pixel, count in distinct_pixels.items():
        if count > greatest_count[0]:
            greatest_count = (count, pixel)
    print(f'Most common pixel: {greatest_count[1]} => {greatest_count[0]}')
    random.seed(0)#for consistency
    k_means = generate_ks(k_count)    #initialize k-means
    k_means = position_pixels(k_means, pixels)
    averages = average(k_means)
    #print(averages)
    passes = 0
    while True:
        passes += 1
        for n,aver in enumerate(averages):
            if len(aver) == 0:
                averages[n] = (random.choice(pixels))
        for i in range(k_count):
            k_means[i][0] = averages[i]
        k_means = position_pixels(k_means, pixels)
        new_averages = average(k_means)
        if new_averages == averages:
            break
        averages = new_averages
    if DEBUG:
        print(passes)
    print('Final Means:')
    for n, k in enumerate(k_means):
        #print(f'{n+1}: {(int(round(k[0][0])), int(round(k[0][1])), int(round(k[0][2])))} => {len(k[1])}')
        print(f'{n + 1}: {(k[0][0], k[0][1], k[0][2])} => {len(k[1])}')
    #print(sum(len(k[1]) for k in k_means))

    compressed_img = Image.new('RGB', (img.width, img.height))
    for color, pixelset in k_means:
        color = (int(round(color[0])), int(round(color[1])), int(round(color[2])))
        for pixel in pixelset:
            compressed_img.putpixel((pixel % img.width, pixel // img.width), color)
    if DEBUG:
        #compressed_img.show()
        compressed_img.save("kmeans/{}{}.png".format('2022nbonanno', int(time.time())), "PNG")
    else:
        compressed_img.save("kmeans/{}.png".format('2022nbonanno'), "PNG")

    #count regions using a BFS algorithm

    pixels = compressed_img.load()
    debug_pixels = list(compressed_img.getdata())
    visited = set()
    regions = []
    for h in range(compressed_img.height):
        for w in range(compressed_img.width):
            if (w,h) in visited:
                continue
            search_space = [(w,h)]
            region = []
            current_color = pixels[w,h]

            while (search_space):
                pos = search_space.pop()
                if pos in visited:
                    continue
                visited.add(pos)
                region.append(pos)
                x, y = pos[0], pos[1]
                for k in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if (0 <= (y+k) and (y+k) < compressed_img.height) and (0 <= (x+j) and (x+j) < compressed_img.width) and (pixels[(x+j), (y+k)] == current_color):
                            search_space.append((x + j, y + k))

            if len(region) > 0:
                regions.append((current_color, region))
    region_counts = []
    for color, pixels in k_means:
        count = 0
        color = (int(round(color[0])), int(round(color[1])), int(round(color[2])))
        for col, region in regions:
            if col == color:
                count += 1
        region_counts.append(count)

    print(f"Region counts: {', '.join(map(str, region_counts))}")
    if DEBUG:
        print(time.time() - start)








def position_pixels(k_means, pixels):
    closest = closest_k
    new_k_means = [[k[0], []] for k in k_means]
    for n,pixel in enumerate(pixels):
        new_k_means[closest(k_means, pixel)][1].append(n)
    return new_k_means


def average(k_means):
    return [[sum(z)/len(z) for z in zip(*list(map(pixels.__getitem__, k[1])))] for k in k_means]


def closest_k(k_means, point):
    closest = (0, 1000000)
    dist = math.dist

    for n,k in enumerate(k_means):
        if (u:=dist(k[0], point)) < closest[1]:
            closest = (n, u)

    return closest[0]
    #return min((dist(k[0], point), n) for n,k in enumerate(k_means))[1]


import random
def generate_ks(k_num):
    global pixels
    return [[random.choice(pixels), []] for i in range(k_num)]#k_mean, points




if __name__ == '__main__':
    main()


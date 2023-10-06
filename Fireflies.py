import sys;args = sys.argv[1:]
# Nicholas Bonanno, pd. 6
import random, math, time
import tkinter as tk


def GetDimensions(N):
    global w, h
    h = int(math.sqrt(N))
    while N % h != 0:
        h -= 1
    w = N // h

    w, h = list(reversed(sorted([w, h])))
    return w, h


def ProcessArgs():
    global args, firefly_count, time_ratio, bump_amount, threshold
    firefly_count = int(args[0])
    time_ratio = float(args[1])
    bump_amount = float(args[2])
    threshold = float(args[3])


def InitTK():
    global firefly_count, window, canvas, shapes, w, h
    window = tk.Tk()
    window.update()
    pixel_size = int(window.winfo_screenheight() * .8 / h)#scales the wide length of each firefly pixel so that the overall tkinter canvas is ~.8 of the total screen height
    width_pixels, height_pixels = w, h
    pixel_width, pixel_height = width_pixels * pixel_size, height_pixels * pixel_size
    side_length_squares = math.ceil(math.sqrt(firefly_count))
    canvas = tk.Canvas(window, width=pixel_width, height=pixel_height, bg='black')
    canvas.pack()
    shapes = []
    for y in range(height_pixels):#adds the firefly pixels to the canvas
        for x in range(width_pixels):
            shapes.append(rec := canvas.create_rectangle(x * pixel_size, y * pixel_size, (x + 1) * pixel_size, (y + 1) * pixel_size, fill=f"black"))


position = 0
update_time = 0
frame_time = 0
def update(schedule):#updates the firefly pixels with the new firefly potentials
    global window, canvas, shapes, potentials, trips, position, threshold, update_time, frame_time
    fireflies = potentials[position]
    tripped = trips[position]
    position += 1
    for n, rec in enumerate(shapes):
        if n == len(fireflies):
            break
        color_coeff = (fireflies[n] / threshold)
        canvas.itemconfig(rec, fill=f"#{((u:=hex(int(255 - 255 * color_coeff)))[u.find('x') + 1 :]).rjust(2, '0')}{((u:=hex(int(255 - 255 * color_coeff)))[u.find('x') + 1 :]).rjust(2, '0')}00")
    if position != len(potentials) and schedule:
        window.after(update_time, update)
    #print(time.time() - frame_time)
    frame_time = time.time()


def update_fireflies_normal():#standard firefly update method that doesn't care about distance
    #this is impractical for large numbers of fireflies due to the increased convergence speed unless the bump amount is similarly decreased
    global args, firefly_count, time_ratio, bump_amount, threshold, window, potentials, trips, update_time, converges, fireflies, steps, DEBUG

    tripped = [False] * firefly_count  # to know if the firefly is flashing this time step
    for i in range(firefly_count):
        fireflies[i] += time_ratio * (1 - fireflies[i])
    while any(potential >= threshold for potential in fireflies):
        for i in range(firefly_count):
            if fireflies[i] >= threshold:  # firefly is going off
                tripped[i] = True
                fireflies[i] = 0
                for j in range(firefly_count):
                    fireflies[j] += bump_amount * (not tripped[j])  # don't bump if it's going off this time step
    steps += 1
    trips.append(tripped)
    potentials.append(list(fireflies))
    if all(potential == 0 for potential in fireflies):
        converges += 1
    if converges == 3:
        return False
    return True


def distance_squared(pos1, pos2):
    global w, h
    if pos1 == pos2:
        return 1
    dist = (((pos1 % w) - (pos2 % w))**2 + ((pos1 // w) - (pos2 // w))**2)
    #print(dist)
    return dist


def update_fireflies_dist():#same as standard but the bump is divided by the distance squared between the two fireflies
    #the slowest method by far with a greater than 100x difference from standard or near
    global args, firefly_count, time_ratio, bump_amount, threshold, window, potentials, trips, update_time, converges, fireflies, steps, DEBUG

    tripped = [False] * firefly_count  # to know if the firefly is flashing this time step
    for i in range(firefly_count):
        fireflies[i] += time_ratio * (1 - fireflies[i])
    while any(potential >= threshold for potential in fireflies):
        for i in range(firefly_count):
            if fireflies[i] >= threshold:  # firefly is going off
                tripped[i] = True
                fireflies[i] = 0
                for j in range(firefly_count):
                    bump = bump_amount * (not tripped[j]) / distance_squared(i, j)  # don't bump if it's going off this time step
                    #print(bump)
                    fireflies[j] += bump
    steps += 1
    trips.append(tripped)
    potentials.append(list(fireflies))
    if all(potential == 0 for potential in fireflies):
        converges += 1
    if converges == 3:
        return False
    return True


def get_surrounding_fireflies(pos):
    global args, firefly_count, time_ratio, bump_amount, threshold, window, potentials, trips, update_time, converges, fireflies, steps, DEBUG, w, h
    x = pos % w
    y = pos // w
    surrounding = []
    if x + 1 < w:
        surrounding.append(y * w + (x + 1))
    if x - 1 >= 0:
        surrounding.append(y * w + (x - 1))
    if y + 1 < h:
        surrounding.append((y + 1) * w + x)
    if y - 1 >= 0:
        surrounding.append((y - 1) * w + x)
    return surrounding


def update_fireflies_near():#same as standard but the only fireflies that a firefly can bump are distance 1 away
    #the fastest of the two non-standard methods, but still slower than normal. I suspect it scales better when handling similar numbers of steps, though
    global args, firefly_count, time_ratio, bump_amount, threshold, window, potentials, trips, update_time, converges, fireflies, steps, DEBUG

    tripped = [False] * firefly_count  # to know if the firefly is flashing this time step
    for i in range(firefly_count):
        fireflies[i] += time_ratio * (1 - fireflies[i])
    while any(potential >= threshold for potential in fireflies):
        for i in range(firefly_count):
            if fireflies[i] >= threshold:  # firefly is going off
                tripped[i] = True
                fireflies[i] = 0
                for j in get_surrounding_fireflies(i):
                    fireflies[j] += bump_amount * (not tripped[j])  # don't bump if it's going off this time step
    steps += 1
    trips.append(tripped)
    potentials.append(list(fireflies))
    if all(potential == 0 for potential in fireflies):
        converges += 1
    if converges == 3:
        return False
    return True


def tkinter_loop():
    global window, canvas, shapes, potentials, trips, position, threshold, update_time, frame_time
    while position < len(potentials):
        start = time.time()
        update(False)
        canvas.update()
        while time.time() - start < update_time / 1000:
            pass


def main():
    global args, firefly_count, time_ratio, bump_amount, threshold, window, potentials, trips, update_time, converges, fireflies, steps, DEBUG, w, h
    start = time.time()
    #args = ['10000', '0.05', '.01', '.95']
    DEBUG = not args
    args = ['350', '0.05', '.0002', '.95'] if DEBUG else args
    ProcessArgs()
    random.seed(1)
    fireflies = [random.random() for i in range(firefly_count)]
    GetDimensions(firefly_count)
    steps = 0
    potentials = [list(fireflies)]
    trips = [[]]
    converges = 0
    while update_fireflies_normal():
        pass

    print(f'{steps} steps')
    target_time = 5
    update_time = int(target_time / len(potentials) * 1000)#set to try to ensure a 25 second runtime
    print(update_time * len(potentials) / 1000)#in seconds
    if DEBUG:
        print(f'done calculating in {time.time() - start} seconds')
    start = time.time()
    InitTK()
    update(False)
    tkinter_loop()
    if DEBUG:
        print(f'finished displaying in {time.time() - start} seconds compared to the targeted {target_time} seconds')
    window.mainloop()


if __name__ == '__main__':
    main()

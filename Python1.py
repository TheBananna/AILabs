#Nicholas Bonanno
#Python 1
#I'm not sure if I actually submitted this earlier, so I'm doing it again now

#Warmup 1
def sleep_in(weekday, vacation):
    return (not weekday) or vacation


def monkey_trouble(a_smile, b_smile):
    return not (a_smile ^ b_smile)


def sum_double(a, b):
    return 4 * a if a == b else a + b


def diff21(n):
    return 2 * abs(n - 21) if n > 21 else abs(n - 21)


def parrot_trouble(talking, hour):
    return talking and (7 > hour or hour > 20)


def makes10(a, b):
    return a == 10 or b == 10 or a + b == 10


def near_hundred(n):
    return abs(n - 100) <= 10 or abs(n - 200) <= 10


def pos_neg(a, b, negative):
    return (a < 0 and b < 0) if negative else ((a < 0) ^ (b < 0) and not (a == 0 or b == 0))


#String 1
def hello_name(name):
    return f'Hello {name}!'


def make_abba(a, b):
    return f'{a}{b}{b}{a}'


def make_tags(tag, word):
    return f'<{tag}>{word}</{tag}>'


def make_out_word(out, word):
    return f'{out[:len(out)//2]}{word}{out[len(out)//2:]}'


def extra_end(str):
    return str[len(str) - 2:] * 3


def first_two(str):
    return str[:2]


def first_half(str):
    return str[:len(str)//2]


def without_end(str):
    return str[1:len(str)-1]


#List 1
def first_last6(nums):
    return ((nums[0]) == 6 or (nums[0]) == '6') or ((nums[len(nums) - 1]) == 6 or nums[len(nums) - 1] == '6')


def same_first_last(nums):
    return len(nums) >= 1 and nums[0] == nums[len(nums) - 1]


def make_pi(n):
    return [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7][0:n]


def common_end(a, b):
    return a[0] == b[0] or a[len(a) - 1] == b[len(b) - 1]


def sum3(nums):
    return sum(nums)


def rotate_left3(nums):
    return nums[1:] + nums[:1]


def reverse3(nums):
    return list(reversed(nums))


def max_end3(nums):
    return [(nums[0] if nums[0] > nums[len(nums) - 1] else nums[len(nums) - 1]) for i in range(len(nums))]


#Logic 1
def cigar_party(cigars, is_weekend):
    return cigars >= 40 if is_weekend else 40 <= cigars <= 60


def date_fashion(you, date):
    return 0 if (you <= 2 or date <= 2) else (2 if (you >= 8 or date >= 8) else 1)


def squirrel_play(temp, is_summer):
    return 60 <= temp <= 100 if is_summer else 60 <= temp <= 90


def caught_speeding(speed, is_birthday):
    return 0 if speed <= (60 + is_birthday * 5) else (1 if speed <= (80 + is_birthday * 5) else 2)


def sorta_sum(a, b):
    return 20 if 10 <= a+b <= 20 else a + b


def alarm_clock(day, vacation):
    return 'off' if (not (0 < day < 6)) and vacation else ('10:00' if (not (0 < day < 6)) ^ vacation else '7:00')


def love6(a, b):
    return a == 6 or b == 6 or abs(a - b) == 6 or a + b == 6


def in1to10(n, outside_mode):
    return n <= 1 or n >= 10 if outside_mode else 1 <= n <= 10

def test():
    print(dir(globals()))
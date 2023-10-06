#Nicholas Bonanno
#Python 2

#Warmup 2
def string_times(s, n):
    return s*n


def front_times(s, n):
    return s[:3]*n


def string_bits(s):
    return s[::2]


def string_splosion(s):
    return''.join([s[:i+1]for i in range(len(s))])


def last2(s):
    return len([i for i in zip(s[:-2],s[1:])if i[0]+i[1]==s[-2:]])


def array_count9(n):
    return n.count(9)
    #return len([i for i in nums if i==9])


def array_front9(n):
    return 9in n[:4]
    #return n[:4].count(9)>0
    #return bool([i for i in n[:4] if i==9])


def array123(n):
    #return bool((' '+' '.join(map(str, n))+' ').count(' 1 2 3 '))
    #return(' '+' '.join(map(str, n))+' ').count(' 1 2 3 ')!=0
    return' 1 2 3 'in' '+' '.join(map(str, n))+' '


def string_match(a, b):
    return len([i for i in range(min(len(a)-1,len(b)-1))if a[i:i+2]==b[i:i+2]])


#Logic2
def make_bricks(s, b, g):
    return g-min(g//5,b)*5<=s


def lone_sum(a, b, c):
    return sum([i for i in[a,b,c]if[a,b,c].count(i)==1])


def lucky_sum(a, b, c):
    #return(a!=13)*a+(a!=13and b!=13)*b+(a!=13and b!=13and c!=13)*c
    return(m:=a!=13)*a+(n:=m and b!=13)*b+(n and c!=13)*c


def no_teen_sum(a, b, c):
    return sum([i for i in[a,b,c]if i<13or i>19or i==15or i==16])


#fails tests on CodingBat, but does not fail the same ones on my computer
def round_sum(a, b, c):
    return sum([int(round(i/10+.01)*10)for i in[a,b,c]])


def close_far(a, b, c):
    return(abs(a-b)<=1)^(abs(a-c)<=1)and abs(b-c)>=2
    #return(m:=abs(a-b)<=1)^(n:=abs(a-c)<=1)and~m+1^~n+1and(abs(b-c)>=2)
    #return(abs(a-b)<=1)^(abs(a-c)<=1)and max(abs(a-b),abs(a-c))>=2and(abs(b-c)>=2)
    #return(abs(a-b)<=1)^(abs(a-c)<=1)and(abs(a-b)>=2)^(abs(a-c)>=2)and(abs(b-c)>=2)


def make_chocolate(s, b, g):
    #return(g-min(g//5,b)*5,-1)[g-min(g//5,b)*5>s]
    return(m:=g-min(g//5,b)*5,-1)[m>s]


#String 2
def double_char(s):
    return''.join([''.join(i)for i in zip(s,s)])


def count_hi(s):
    return s.count('hi')


def cat_dog(s):
    return s.count('cat')==s.count('dog')


def count_code(s):
    return len([i for i in ('  '+s).split('co')if i[1:2]=='e'])
    #return len([i for i in range(len(s)-3) if s[i:i+2]=='co'and s[i+3]=='e'])


def end_other(a, b):
    return a.lower().endswith(b.lower())or b.lower().endswith(a.lower())


def xyz_there(s):
    #return bool([i for i in range(-1,len(s)) if s[i:i+1]!='.'and s[i+1:i+4]=='xyz'])
    return'xyz'in' '.join(s.split('.xyz'))


#List 2
def count_evens(n):
    return len([i for i in n if i%2==0])


def big_diff(n):
    return max(n)-min(n)


def centered_average(n):
    return (sum(n)-max(n)-min(n))//(len(n)-2)
   #return sum(n:=sorted(n)[1:-1])//len(n)# best


def sum13(n):
    return sum([n[i]for i in range(len(n))if n[i]!=13and n[max(i-1,0)]!=13])
   #return sum(z[0]for z in zip(nums,[0]+nums)if{13}-{*z})# best


def sum67(n):
    a,s=True,0
    for i in n:
        a=False if i==6else a
        s+=i if a else 0
        a=True if i==7else a
    return s
   #return sum(n*((f:=(n[-(n!=6)+i::-1]+[7,6]).index)(7)<f(6))for i in,n in enumerate(n))# normal best
   #return(b:=1)*sum(x*(x!=7or b)*(b:=[[b,1][x==7],0][x==6])for x in n)# new best original
   #return(b:=1)*sum(x*b*(b:=[x==7,x!=6][b])for x in n)# new best optimized


def has22(n):
    return' 2 2 'in' '+' '.join(map(str,n))+' '

import sys; args = sys.argv[1:]
idx = int(args[0])-50

myRegexLst = [
    r"/\w*(\w)\w*\1\w*/i",                  #/(\w)+\w*\1\w*/i
    r"/\w*(\w)\w*(\1\w*){3}/i",             #/(\w)+(\w*\1\w*){3}/i
    r"/^([10])[10]*\1$|^[10]$/",            #/^(1|0)(0*1*\1)*$/
    r"/\b(?=\w*cat)\w{6}\b/i",              #assume ideal
    r"/\b(?=\w*bri)(?=\w*ing)\w{5,9}\b/i",  #ideal
    r"/\b((?!cat)\w){6}\b/i",               #ideal
    r"/\b((\w)(?!\w*\2))+\b/i",             #/(?!(\w)*\w*\1)\b\w+/i
    r"/^(?![10]*10011)[10]*$/",             #/^(0|1(?!0011))*$/
    r"/\b\w*(([aeiou])(?!\2)){2}\w*/i",     #/\w*(?!(.)\1)[aeiou]{2}\w*/i
    r"/^((?!101|111)[10])*$/"               #/^(0|1(?!.1))*$/
]

if idx < len(myRegexLst):
  print(myRegexLst[idx])


print(sum(map(len, myRegexLst)))
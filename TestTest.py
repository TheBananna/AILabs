import sys; args = sys.argv[1:]
idx = int(args[0])-70 if args else -1
#Nicholas Bonanno
#Regex 5

#will match on partial word matches so some start and end anchors might not be needed
myRegexLst = [
    r"/^(?=[a-z]*$)(?=\w*a)(?=\w*e)(?=\w*i)(?=\w*o)(?=\w*u)\w*$/m",                #70
    r"/^(?=[a-z]*$)([^aeiou\n]*[aeoiu][^aeiou\n]*){5}$/m",                                        #71
    r"//m",  #need to account for w and maybe y as vowels  #72
    r"//m",                                      #73
    r"/^(?=[a-z]*$)[^bt\n]*(bt|tb)[^bt\n]*$/m",                                         #74
    r"/^(?=[a-z]*$)\w*(\w)\1{1,}/m",                                               #75
    r"/^(?=[a-z]*$)\w*(\w)(\w*\1){5,}/m",                                          #76
    r"/^(?=[a-z]*$)\w*((\w)\2){3,}/m",                                          #77
    r"/^(?=[a-z]*$)\w*(\w*[^aeiou\n]){13,}/m",                                   #78
    r"/^(?=[a-z]*$)((\w)(?!(\w*\2\w*){2,}$))+$/m"                                            #79
]
if idx == -1:
    print(sum(map(len, myRegexLst)))
elif idx < len(myRegexLst):
  print(myRegexLst[idx])


import sys; args = sys.argv[1:]
idx = int(args[0])-30

myRegexLst = [
    r"/^0{1}$|^1{1}0{1}0{1}$|^1{1}0{1}1{1}$/",
    r"/^[10]*$/",
    r"/0$/",
    r"/\b\S*[aeiou]\w*[aeiou]\w*\b/i",
    r"/^1[10]*0$|^0$/",
    r"/^[10]*110[10]*$/",
    r"/^.{2,4}$/s",
    r"/^\d{3}\s*-{0,1}\s*\d{2}\s*-{0,1}\s*\d{4}$/",
    r"/^.*?d\w*/mi",
    r"//"
]

if idx < len(myRegexLst):
  print(myRegexLst[idx])

import sys; args = sys.argv[1:]
idx = int(args[0])-40

myRegexLst = [
    r"/^[x.o]{64}$/i",
    r"/^[xo]*\.[xo]*$/i",
    r"/^\.[xo.]*$|^[xo.]*\.$|^x+o*\.[xo.]*$|^[xo.]*?\.o*x+$/im",
    r"/^(..)*.$/s",
    r"/^(0([10]{2})*)$|^(1([10]{2})*[10])$/",
    r"/\w*(ae|ai|ao|au|ea|ei|eo|eu|ia|ie|io|iu|oa|oe|oi|ou|ua|ue|ui|uo)\w*/i",
    r"/^1*$|^1?(01?)+1*$|^0*$/",
    r"/^[bc]+a?[bc]+$|^a$|^a[bc]*$|^[bc]*a$|^[bc]+$/",
    r"/^([bc]*a[bc]*a[bc]*)+$|^[bc]+$/",
    r"//m"
]

if idx < len(myRegexLst):
  print(myRegexLst[idx])


print(sum(map(len, myRegexLst)))
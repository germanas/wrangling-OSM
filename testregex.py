import re
#pattern = re.compile("^([A-Z][0-9]+)+$")
#if pattern.match('A1B2'):


pattern = re.compile((r'/([\w\s])*g\.$/g'))
if pattern.match('Sudu g.'):
    print 'fuck'


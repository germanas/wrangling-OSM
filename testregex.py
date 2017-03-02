#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
#pattern = re.compile("^([A-Z][0-9]+)+$")
#if pattern.match('A1B2'):


pattern = re.compile((r'([\w\s])*g\.$'))
if pattern.match(('gatv g.')):
    print 'Veikia'


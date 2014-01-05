# -*- coding: utf-8 -*-
# Author: Bin LI (richardustc@gmail.com)
# All rights reserved.

# 本文件用于测试JsonParser.py

from JsonParser import *
import sys
import pdb

testcases = [
'{}',
'{"number":1}',
'{"string":"string"}',
'{"true": true}',
'{"false": false}',
'{"null": null}',
'{"array": []}',
'{"array":[1, "s" , true, false, null]}',
'{"array":[[1, 2, 3], [true, false], [null] ]}',
'{"array":[{"number":1}, {"string":"string"} ]}',
'{"object": {}}',
'{"object": {"array": [1, true, {"object": "object"}]}}'
]

print "Start testing..."
p = JsonParser()
for s in testcases:
	p.load(s)
print "End testing..."

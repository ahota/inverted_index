#!/bin/bash

javac -classpath ../../hadoop/hadoop-1.2.1/hadoop-core-1.2.1.jar -d classes $1
jar -cvf ./invertedindex.jar -C classes .

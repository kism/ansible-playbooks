#!/bin/sh
/bin/df | grep "/srv" | sort -k4 -n | head -1 | awk '{print $2" "$4}'
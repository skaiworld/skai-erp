#!/bin/bash

bench schedule &
P1=$!
bench worker --queue long,default,short &
P2=$!
wait $P1 $P2

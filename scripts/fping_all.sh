#!/bin/bash
i=0

while true
do
  echo Ping Check Iteration: $i
  fping -f ip_list.txt
  sleep 2
  ((i++))
  clear
done

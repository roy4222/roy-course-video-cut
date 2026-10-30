#!/bin/sh
# sheet.sh dir out.jpg : tile all t_*.jpg (sorted by time) 3 columns at 640 wide
d=$1; o=$2; SL="${PIPELINE_TMP:-/tmp}/sl.txt"; ls $d/t_*.jpg | sort -t_ -k2 -g > "$SL"
n=$(wc -l < "$SL"); rows=$(( (n+2)/3 ))
args=""; i=0; for f in $(cat "$SL"); do args="$args -i $f"; i=$((i+1)); done
ffmpeg -loglevel error -y $args -filter_complex "$(i=0; for f in $(cat "$SL"); do printf "[$i]scale=640:360[s$i];"; i=$((i+1)); done; i=0; for f in $(cat "$SL"); do printf "[s$i]"; i=$((i+1)); done; printf "xstack=inputs=$n:layout="; i=0; for f in $(cat "$SL"); do c=$((i%3)); r=$((i/3)); printf "%s_%s" $((c*640)) $((r*360)); i=$((i+1)); [ $i -lt $n ] && printf "|"; done)" -frames:v 1 $o

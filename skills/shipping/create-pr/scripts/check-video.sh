#!/usr/bin/env bash
# Checks a PR or bug video before it is attached. Needs ffmpeg and ffprobe.
# FAIL (exit 1): file over the upload limit, or the page fills only part of the frame.
# WARN: each stretch where nothing on screen changes for longer than STILL_S seconds.
set -euo pipefail
f="${1:?usage: check-video.sh <video> [limit_mb]}"
limit_mb="${2:-10}"
still_s="${STILL_S:-3}"
fail=0

read -r w h fps < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate \
  -of csv=p=0 "$f" | tr ',' ' ')
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
mb=$(awk -v b="$(wc -c < "$f")" 'BEGIN { printf "%.1f", b / 1048576 }')
echo "video ${w}x${h}, ${fps} fps, ${dur%.*} s, ${mb} MB"
if awk -v m="$mb" -v l="$limit_mb" 'BEGIN { exit !(m > l) }'; then
  echo "FAIL size: ${mb} MB is over the ${limit_mb} MB upload limit"; fail=1
fi

# A recorder that got smaller frames than its size pads the bottom-right with flat grey.
grey=$(ffmpeg -hide_banner -i "$f" -vf "fps=1,crop=40:40:iw-40:ih-40,signalstats,metadata=print" -f null - 2>&1 \
  | awk -F= '/YMIN=/{ymin=$2} /YMAX=/{ymax=$2} /UAVG=/{u=$2} /VAVG=/{v=$2; n++;
      if (ymax-ymin<=3 && u>124 && u<132 && v>124 && v<132 && ymin>90 && ymax<160) g++}
      END { printf "%d %d", g+0, n }')
read -r g n <<< "$grey"
if [ "$n" -gt 0 ] && [ $((g * 2)) -gt "$n" ]; then
  echo "FAIL fill: ${g} of ${n} sampled frames have grey padding; another screencast (tracing?) set the frame size"; fail=1
fi

ffmpeg -hide_banner -i "$f" -vf "mpdecimate=hi=768:lo=320:frac=0.1,showinfo" -f null - 2>&1 \
  | grep -o "pts_time:[0-9.]*" | cut -d: -f2 \
  | awk -v end="$dur" -v s="$still_s" '{ if (NR>1 && $1-p>s) printf "WARN still %.1f-%.1f s (%.1f s)\n", p, $1, $1-p; p=$1 }
      END { if (end-p>s) printf "WARN still %.1f-%.1f s (%.1f s) at the end\n", p, end, end-p }'

[ "$fail" -eq 0 ] && echo "PASS size and fill; read each WARN still: a chapter card is fine, a frozen step is not"
exit "$fail"

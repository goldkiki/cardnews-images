#!/bin/bash
# usage: post.sh <date> <sport> <n_images> <repo_dir>
set -u
DATE=$1; SPORT=$2; N=$3; REPO=$4
BASE=https://raw.githubusercontent.com/goldkiki/cardnews-images/main/$DATE/$SPORT
H="Authorization: Bearer proxy-injected"
jid(){ python3 -I -c 'import sys,json;print(json.load(sys.stdin).get("id",""))'; }
fld(){ python3 -I -c 'import sys,json;print(json.load(sys.stdin).get(sys.argv[1],"?"))' "$1"; }
wait_done(){ # $1 url-base, $2 id, $3 field
  local i st; sleep 30
  for i in 1 2 3 4 5 6; do st=$(curl -sS -H "$H" "$1/$2?fields=$3" | fld "$3"); [ "$st" = FINISHED ] && return 0
    [ "$st" = ERROR ] && { echo "  container ERROR"; return 1; }; sleep 30; done; echo "  status timeout ($st)"; return 1; }

echo "== threads"
G=https://graph.threads.net/v1.0; U=29150898491233057; kids=(); ok=1
for i in $(seq -w 1 $N); do i=$(printf %02d $((10#$i)))
  r=$(curl -sS -H "$H" -X POST "$G/$U/threads" -d media_type=IMAGE -d is_carousel_item=true --data-urlencode "image_url=$BASE/$i.png")
  id=$(echo "$r" | jid); [ -z "$id" ] && { echo "  item $i failed: $r"; ok=0; break; }; kids+=($id); done
if [ $ok = 1 ]; then
  r=$(curl -sS -H "$H" -X POST "$G/$U/threads" -d media_type=CAROUSEL --data-urlencode "children=$(IFS=,; echo "${kids[*]}")" --data-urlencode "text@$REPO/$DATE/$SPORT/caption_threads.txt")
  cid=$(echo "$r" | jid)
  if [ -z "$cid" ]; then echo "  carousel failed: $r"; elif wait_done $G $cid status; then
    r=$(curl -sS -H "$H" -X POST "$G/$U/threads_publish" -d creation_id=$cid); mid=$(echo "$r" | jid)
    [ -z "$mid" ] && echo "  publish failed: $r" || curl -sS -H "$H" "$G/$mid?fields=id,permalink,timestamp"; echo
  fi
fi

echo "== instagram"
G=https://graph.facebook.com/v27.0; U=17841413686314660; kids=(); ok=1
for i in $(seq 1 $N); do i=$(printf %02d $i)
  r=$(curl -sS -H "$H" -X POST "$G/$U/media" -d is_carousel_item=true --data-urlencode "image_url=$BASE/$i.png")
  id=$(echo "$r" | jid); [ -z "$id" ] && { echo "  item $i failed: $r"; ok=0; break; }; kids+=($id); done
if [ $ok = 1 ]; then
  r=$(curl -sS -H "$H" -X POST "$G/$U/media" -d media_type=CAROUSEL --data-urlencode "children=$(IFS=,; echo "${kids[*]}")" --data-urlencode "caption@$REPO/$DATE/$SPORT/caption_instagram.txt")
  cid=$(echo "$r" | jid)
  if [ -z "$cid" ]; then echo "  carousel failed: $r"; elif wait_done $G $cid status_code; then
    r=$(curl -sS -H "$H" -X POST "$G/$U/media_publish" -d creation_id=$cid); mid=$(echo "$r" | jid)
    [ -z "$mid" ] && echo "  publish failed: $r" || curl -sS -H "$H" "$G/$mid?fields=id,permalink,timestamp"; echo
  fi
fi

#!/bin/sh
# Make a folder on Alliance /project private to you + your PI (and anyone you add),
# instead of readable by the whole allocation group. Uses POSIX ACLs, with default ACLs
# so new files and folders inherit the same access.
#
#   sh fir_share.sh [DIR]                 apply (DIR defaults to $PROJECTS_ROOT)
#   sh fir_share.sh --check [DIR]         report only; lists items the PI can't reach
#   sh fir_share.sh --with USER [DIR]     also give USER read/write (repeatable)
#   sh fir_share.sh --pi USER [DIR]       PI username if it can't be read from the path
#
# The PI is read from the path: /project/def-<pi>/... (also rrg-<pi>-xx, rpp-<pi>-xx).
# Safe to re-run; re-run after copying data in with cp -p / rsync -a / tar, which keep
# the source permissions instead of inheriting the defaults.
set -e

check=0; pi=""; extra=""
while [ $# -gt 0 ]; do
    case "$1" in
        --check) check=1 ;;
        --pi)    pi="$2"; shift ;;
        --with)  extra="$extra $2"; shift ;;
        -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
        -*) echo "unknown option: $1" >&2; exit 2 ;;
        *)  dir="$1" ;;
    esac
    shift
done
dir="${dir:-$PROJECTS_ROOT}"
[ -n "$dir" ] || { echo "Give a folder, or set PROJECTS_ROOT." >&2; exit 2; }
[ -d "$dir" ] || { echo "Not a folder: $dir" >&2; exit 2; }
command -v setfacl >/dev/null || { echo "setfacl not found (not on a cluster?)" >&2; exit 2; }

# Detect the PI from the path as typed (the real path may be /project/<gid>/...).
if [ -z "$pi" ]; then
    pi=$(printf '%s\n' "$dir" | sed -n 's#.*/\(def\|rrg\|rpp\)-\([a-z0-9]*\).*#\2#p')
fi
[ -n "$pi" ] || { echo "Can't tell the PI from '$dir'; pass --pi USER." >&2; exit 2; }
real=$(readlink -f "$dir")
me=$(id -un)
users="$pi $extra"
for u in $users; do
    id "$u" >/dev/null 2>&1 || { echo "No such user on this cluster: $u" >&2; exit 2; }
done
[ "$(stat -c %U "$real")" = "$me" ] || { echo "You don't own $real; only the owner can set this." >&2; exit 2; }

if [ "$check" = 1 ]; then
    echo "Access on $real:"
    getfacl -p "$real" 2>/dev/null | grep -v '^#'
    for u in $users; do
        # Items where $u has no entry, or the mask cuts it below read+write.
        missing=$(getfacl -R -p "$real" 2>/dev/null | awk -v u="user:$u:" '
            /^# file: / { if (f != "" && !ok) n++; f = substr($0, 9); ok = 0; next }
            index($0, u) == 1 {
                perm = $0; sub(/^user:[^:]*:/, "", perm)
                if (perm ~ /#effective:/) sub(/.*#effective:/, "", perm)
                if (perm ~ /^rw/) ok = 1
            }
            END { if (f != "" && !ok) n++; print n + 0 }')
        echo "$u: $missing item(s) without read+write"
    done
    # Read the real group/other entries (with ACLs, ls/find group bits show the mask).
    open=$(getfacl -R -p "$real" 2>/dev/null | awk '
        /^# file: / { f = $0 }  /^(group|other)::r/ && f != last { n++; last = f }
        END { print n + 0 }')
    echo "group/others readable: $open item(s)"
    exit 0
fi

echo "Making $real private to $me + $(echo $users | tr ' ' '+') ..."
# 1. Remove group/others first: on ACL'd files chmod rewrites the mask, so it must come
#    before setfacl (which recalculates the mask).
chmod -R go-rwx "$real"
acl=""; dacl="d:u::rwX,d:g::---,d:o::---"
for u in $users; do acl="$acl,u:$u:rwX"; dacl="$dacl,d:u:$u:rwX"; done
acl=${acl#,}
# 2. Read/write for each user (X = enter folders; execute only what already is).
setfacl -R -m "$acl" "$real"
# 3. Defaults on every folder, so new files and folders get the same rules.
find "$real" -type d -exec setfacl -m "$dacl" {} +
# 4. Let them pass through parent folders you own (enter only, no listing).
p=$(dirname "$real")
while [ "$p" != "/" ] && [ "$(stat -c %U "$p" 2>/dev/null)" = "$me" ]; do
    for u in $users; do setfacl -m "u:$u:x" "$p"; done
    p=$(dirname "$p")
done
echo "Done. Check any time with: sh $0 --check $dir"

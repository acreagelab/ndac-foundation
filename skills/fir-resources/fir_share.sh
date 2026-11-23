#!/bin/sh
# Access on Alliance /project that follows each project's security zone (POSIX ACLs).
#
#   sh fir_share.sh [DIR]               apply; DIR = $PROJECTS_ROOT (all projects) or one project
#   sh fir_share.sh --check [DIR]       report only; nothing is changed
#   sh fir_share.sh --with USER [DIR]   also give USER read/write (repeatable), e.g. people
#                                       named in a data-sharing agreement
#   sh fir_share.sh --pi USER [DIR]     PI username if it can't be read from the path
#   sh fir_share.sh --group G [DIR]     allocation group if it can't be read from the path
#
# Who gets what:
#   you, the PI, data managers  read/write everywhere (data managers: fir_share.conf)
#   and --with users
#   the allocation group        read-only (read code and data; no edit, delete or new
#                               files) on projects whose CLAUDE.md zone is A_Public or
#                               B_Internal; nothing on C_Limited / D_Restric / unset (TODO)
#                               projects, or on folders that aren't projects
#   everyone else               nothing
# The group can list the projects root (project names only) but not change it. New items
# there start private until this script runs (fail closed). Re-run after creating a project, after
# changing its zone, and after copying data in with cp -p / rsync -a / tar.
# The allocation and PI come from the path: /project/def-<pi>/... (also rrg-/rpp-).
set -e

check=0; pi=""; alloc=""; extra=""; dir=""
while [ $# -gt 0 ]; do
    case "$1" in
        --check) check=1 ;;
        --pi)    pi="$2"; shift ;;
        --group) alloc="$2"; shift ;;
        --with)  extra="$extra $2"; shift ;;
        -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
        -*) echo "unknown option: $1" >&2; exit 2 ;;
        *)  dir="$1" ;;
    esac
    shift
done
dir="${dir:-$PROJECTS_ROOT}"
[ -n "$dir" ] || { echo "Give a folder, or set PROJECTS_ROOT." >&2; exit 2; }
[ -d "$dir" ] || { echo "Not a folder: $dir" >&2; exit 2; }
command -v setfacl >/dev/null || { echo "setfacl not found (not on a cluster?)" >&2; exit 2; }

# Allocation group and PI from the path as typed (the real path may be /project/<gid>/...).
from_path=$(printf '%s\n' "$dir" | sed -n 's#.*/\(\(def\|rrg\|rpp\)-[a-z0-9-]*\).*#\1#p')
[ -n "$alloc" ] || alloc="$from_path"
[ -n "$pi" ] || pi=$(printf '%s\n' "$from_path" | sed -n 's/^[a-z]*-\([a-z0-9]*\).*/\1/p')
[ -n "$alloc" ] && [ -n "$pi" ] || { echo "Can't find def-<pi> in '$dir'; use the /project/def-<pi>/... path, or --group and --pi." >&2; exit 2; }
getent group "$alloc" >/dev/null || { echo "No group '$alloc' on this cluster." >&2; exit 2; }
real=$(readlink -f "$dir")
me=$(id -un)
# Data managers for this allocation (fir_share.conf next to this script).
conf="$(dirname "$0")/fir_share.conf"
managers=""
[ -f "$conf" ] && managers=$(awk -v a="$alloc" '$1 == a { $1 = ""; print }' "$conf")
users=""
for u in $pi $managers $extra; do  # de-duplicate; you already own your files
    [ "$u" = "$me" ] && continue
    case " $users " in *" $u "*) ;; *) users="$users $u" ;; esac
done
users=${users# }
[ -n "$users" ] || { echo "Nobody to share with (you are the PI and the only data manager)." >&2; exit 2; }
for u in $users; do
    id "$u" >/dev/null 2>&1 || { echo "No such user on this cluster: $u" >&2; exit 2; }
done
[ "$(stat -c %U "$real")" = "$me" ] || { echo "You don't own $real; only the owner can set this." >&2; exit 2; }

# One project, or the projects root? Refuse a sub-folder of a project: its access follows
# the whole project, so treating it as a root would lock part of the project down.
if [ -f "$real/CLAUDE.md" ]; then
    mode=project
else
    mode=root; p=$(dirname "$real")
    while [ "$p" != "/" ]; do
        [ -f "$p/CLAUDE.md" ] && { echo "$real is inside project $p; run on $p instead." >&2; exit 2; }
        p=$(dirname "$p")
    done
fi

zone_of() {  # zone from the project's CLAUDE.md; "-" if not a project, TODO if unset
    [ -f "$1/CLAUDE.md" ] || { echo "-"; return; }
    z=$(sed -n 's/.*Security zone of inputs:[ `]*\([A-Za-z_]*\).*/\1/p' "$1/CLAUDE.md" | head -1)
    echo "${z:-TODO}"
}
group_perm() {  # what the allocation group gets for a zone
    case "$1" in A_Public|B_Internal) echo "r-X" ;; *) echo "---" ;; esac
}

uacl=""; dacl="d:u::rwX,d:g::---,d:o::---"
for u in $users; do uacl="$uacl,u:$u:rwX"; dacl="$dacl,d:u:$u:rwX"; done
uacl=${uacl#,}
skipped=0

apply_tree() {  # $1 = folder or file, $2 = group permission
    # chmod first: on ACL'd files it rewrites the mask; setfacl then recalculates it.
    chmod -R go-rwx "$1" 2>/dev/null || skipped=1
    setfacl -R -P -m "$uacl,g:$alloc:$2" "$1" 2>/dev/null || skipped=1
    if [ -d "$1" ]; then
        find "$1" -type d -exec setfacl -m "$dacl,d:g:$alloc:$2" {} + 2>/dev/null || skipped=1
    fi
}

# --- check helpers: print up to 5 offending paths, then the count on the last line -------
AWK_EFF='function eff(l) { sub(/^[a-z]+:[^:]*:/, "", l); if (l ~ /#effective:/) sub(/.*#effective:/, "", l); sub(/[ \t].*/, "", l); return l }'
lacking() {  # $1 path, $2 ACL prefix (user:x: / group:x:), $3 1 = also needs write where owner has it
    getfacl -R -P -p "$1" 2>/dev/null | awk -v pre="$2" -v needw="$3" "$AWK_EFF"'
        function done() { if (f == "") return
            if (p !~ /^r/ || (needw && ow && p !~ /^.w/)) { n++; if (n <= 5) print "      " (p == "" ? "none" : p) "  " f } }
        /^# file: / { done(); f = substr($0, 9); p = ""; ow = 0; next }
        /^user::/ { ow = ($0 ~ /^user::.w/) }
        index($0, pre) == 1 { p = eff($0) }
        END { done(); if (n > 5) print "      ... and " n - 5 " more"; print n + 0 }'
}
open_to() {  # $1 path, $2 "-R" or "", $3 perm regex, $4 entry regex: items matching both
    getfacl $2 -P -p "$1" 2>/dev/null | awk -v pr="$3" -v er="$4" "$AWK_EFF"'
        function done() { if (r) { n++; if (n <= 5) print "      " f } }
        /^# file: / { done(); f = substr($0, 9); r = 0; next }
        $0 ~ er { if (eff($0) ~ pr) r = 1 }
        END { done(); if (n > 5) print "      ... and " n - 5 " more"; print n + 0 }'
}
report() {  # $1 label, $2 output of lacking/readable
    n=$(printf '%s\n' "$2" | tail -1)
    printf '    %-34s %s\n' "$1:" "$n"
    [ "$n" = 0 ] || printf '%s\n' "$2" | sed '$d'
    [ "$n" = 0 ] || problems=1
}
check_item() {  # $1 path
    z=$(zone_of "$1"); g=$(group_perm "$z")
    if [ "$g" = "r-X" ]; then what="group read-only"; else what="private"; fi
    echo "  $(basename "$1")  [zone $z -> $what]"
    for u in $users; do report "$u lacks read/write" "$(lacking "$1" "user:$u:" 1)"; done
    if [ "$g" = "r-X" ]; then
        report "$alloc can't read" "$(lacking "$1" "group:$alloc:" 0)"
        report "editable by group/others" "$(open_to "$1" -R '^.w' '^(group|other):[^:]*:')"
        report "readable by others" "$(open_to "$1" -R '^r' '^other::')"
    else
        report "readable by group/others" "$(open_to "$1" -R '^r' '^(group|other):[^:]*:')"
    fi
}

if [ "$check" = 1 ]; then
    problems=0
    echo "Access under $real (allocation $alloc, PI $pi):"
    if [ "$mode" = root ]; then
        echo "  (projects root: group may list names, not change)"
        report "root editable by group/others" "$(open_to "$real" "" '^.w' '^(group|other):[^:]*:')"
        report "root readable by others" "$(open_to "$real" "" '^r' '^other::')"
        for c in "$real"/* "$real"/.[!.]*; do [ -e "$c" ] && check_item "$c"; done
    else
        check_item "$real"
    fi
    [ "$problems" = 0 ] && echo "All as intended." || echo "Fix: sh $0 $dir"
    exit 0
fi

opened=0
if [ "$mode" = root ]; then
    echo "Projects root $real: you + $(echo $users | tr ' ' '+') read/write; $alloc may list it"
    chmod go-rwx "$real"
    setfacl -m "$uacl,g:$alloc:r-x" "$real"
    setfacl -m "$dacl,d:g:$alloc:---" "$real"   # new items private until this script runs
    for c in "$real"/* "$real"/.[!.]*; do
        [ -e "$c" ] || continue
        z=$(zone_of "$c"); g=$(group_perm "$z")
        apply_tree "$c" "$g"
        [ "$g" = "r-X" ] && { opened=1; echo "  $(basename "$c"): zone $z -> $alloc read-only"; } \
                         || echo "  $(basename "$c"): zone $z -> private"
    done
else
    z=$(zone_of "$real"); g=$(group_perm "$z")
    apply_tree "$real" "$g"
    [ "$g" = "r-X" ] && opened=1
    echo "$(basename "$real"): zone $z -> $([ "$g" = "r-X" ] && echo "$alloc read-only" || echo private)"
fi
# Let PI / --with users (and the group, if a project is open to it) pass through parent
# folders you own: enter only, no listing.
pacl=""; for u in $users; do pacl="$pacl,u:$u:x"; done
[ "$opened" = 1 ] && pacl="$pacl,g:$alloc:x"
p=$(dirname "$real")
while [ "$p" != "/" ] && [ "$(stat -c %U "$p" 2>/dev/null)" = "$me" ]; do
    setfacl -m "${pacl#,}" "$p"
    p=$(dirname "$p")
done
[ "$skipped" = 1 ] && echo "Note: some items owned by other users were skipped (only their owner can change them)."
echo "Done. Check any time with: sh $0 --check $dir"

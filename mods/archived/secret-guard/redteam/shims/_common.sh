# sourced by every shim; RT_DATA, RT_REMOTE, RT_SHIMS come from the harness
rt_map() { sed -e "s#/etc/dokploy#$RT_REMOTE/etc/dokploy#g" -e "s#/var/lib/dokploy#$RT_REMOTE/var/lib/dokploy#g" -e "s#/root/#$RT_REMOTE/root/#g"; }
rt_real() { local n=$1; shift; PATH=$(printf '%s' "$PATH" | tr ':' '\n' | grep -vxF "$RT_SHIMS" | paste -sd: -) exec "$n" "$@"; }
rt_internal_url() { local h=${1#*://}; h=${h%%/*}; h=${h##*@}; h=${h%%:*}; case "$h" in 169.254.*|127.*|localhost|*.internal|*.local|*.lan) return 0;; *.*) return 1;; "") return 1;; *) return 0;; esac; }

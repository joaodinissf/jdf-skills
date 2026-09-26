#!/usr/bin/env bash
# Look for an existing Java, tla2tools.jar and Lean toolchain before anyone
# proposes a download. Reads only; installs and writes nothing.
#
#   find-tools.sh           check the usual locations
#   find-tools.sh --deep    also search the home directory (slower)
#
# Prints what it found and the exports check.sh reads (JAVA, TLA2TOOLS).

set -uo pipefail
deep=${1:-}
found() { printf '  found    %-10s %s\n' "$1" "$2"; }
missing() { printf '  missing  %-10s %s\n' "$1" "$2"; }

works() { "$1" -version >/dev/null 2>&1; }

echo "Java"
java_bin=
for candidate in "${JAVA:-}" "$(command -v java 2>/dev/null)" \
  "$( [ -x /usr/libexec/java_home ] && /usr/libexec/java_home 2>/dev/null)/bin/java" \
  /opt/homebrew/opt/openjdk*/bin/java /usr/local/opt/openjdk*/bin/java \
  "$HOME"/.local/share/mise/installs/java/*/bin/java \
  "$HOME"/.sdkman/candidates/java/*/bin/java "$HOME"/.asdf/installs/java/*/bin/java \
  /usr/lib/jvm/*/bin/java; do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  if works "$candidate"; then java_bin=$candidate; break; fi
  missing java "$candidate is present but does not run (a macOS stub launcher?)"
done
if [ -n "$java_bin" ]; then
  found java "$java_bin ($("$java_bin" -version 2>&1 | head -1))"
else
  missing java "no working Java 11+"
fi

echo "TLA+"
jar=
for candidate in "${TLA2TOOLS:-}" "$HOME/.local/share/tla/tla2tools.jar" \
  "$HOME"/.cache/*/tla2tools.jar "$HOME"/.cache/*/*/tla2tools.jar \
  "/Applications/TLA+ Toolbox.app/Contents/Eclipse/tla2tools.jar" \
  "$HOME"/.vscode*/extensions/tlaplus.vscode-ide-*/tools/tla2tools.jar \
  "$HOME"/.cursor/extensions/tlaplus.vscode-ide-*/tools/tla2tools.jar \
  ./tla2tools.jar ./*/.tools/tla2tools.jar; do
  [ -n "$candidate" ] && [ -f "$candidate" ] && { jar=$candidate; break; }
done
if [ -z "$jar" ] && command -v mdfind >/dev/null 2>&1; then
  jar=$(mdfind -name tla2tools.jar 2>/dev/null | grep '/tla2tools\.jar$' | head -1)
fi
skip=(Library node_modules .git .m2 .gradle .npm .cargo .rustup .elan go Pictures Music Movies)
if [ -z "$jar" ] && [ "$deep" = --deep ]; then
  if command -v fd >/dev/null 2>&1; then
    jar=$(fd -H -I -t f --max-depth 7 -g tla2tools.jar ${skip[@]/#/--exclude } "$HOME" 2>/dev/null | head -1)
  else
    prune=(); for d in "${skip[@]}"; do prune+=(-name "$d" -o); done
    jar=$(find "$HOME" -maxdepth 7 \( "${prune[@]}" -false \) -prune -o \
      -name tla2tools.jar -print 2>/dev/null | head -1)
  fi
fi
if [ -n "$jar" ]; then
  version=
  [ -n "$java_bin" ] && version=$("$java_bin" -cp "$jar" tlc2.TLC -version 2>/dev/null | head -1)
  found tla2tools "$jar${version:+ ($version)}"
else
  if [ "$deep" = --deep ]; then hint="not found under \$HOME; ask where it lives"
  else hint="not in the usual places; try --deep, or ask where it lives"; fi
  missing tla2tools "$hint"
fi

echo "Lean"
if command -v elan >/dev/null 2>&1 || [ -x "$HOME/.elan/bin/elan" ]; then
  elan_bin=$(command -v elan || echo "$HOME/.elan/bin/elan")
  found elan "$elan_bin"
  toolchains=$("$elan_bin" toolchain list 2>/dev/null | sed 's/ (default)//')
  if [ -n "$toolchains" ]; then
    while read -r t; do found toolchain "$t"; done <<<"$toolchains"
    "$elan_bin" show 2>/dev/null | grep -q default ||
      echo "           no default toolchain: pin one of these in each project's lean-toolchain"
  else
    missing toolchain "elan has none installed"
  fi
else
  missing elan "no elan; lean and lake may still be on PATH: $(command -v lake 2>/dev/null || echo none)"
fi

echo
[ -n "$java_bin" ] && echo "export JAVA=\"$java_bin\""
[ -n "$jar" ] && echo "export TLA2TOOLS=\"$jar\""
exit 0

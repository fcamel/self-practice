#!/bin/bash

# Show numbers of commits per author.
echo ">>> # of commits"
git shortlog -c -s -n -e | cat
echo

# Show number of files changed per author.
tmpfile=$(mktemp /tmp/abc-script.XXXXXX)
exec 3>"$tmpfile"
rm -f "$tmpfile"

authors=$(git shortlog -c -s -n -e |  awk '{print $NF}' | sort -u)
for a in $authors
do
  n=$(git whatchanged --author="$a" --no-commit-id --name-only | sort -u  | wc -l)
  printf "%6d  %s\n" $n $a >> $tmpfile
done

echo ">>> # of files"
sort -nr $tmpfile

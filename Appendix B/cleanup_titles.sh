#!/usr/local/bin/bash

cd ../results/raw;
rm -rf ../cleaned;
rm -rf ../after_sed;

FILES=(*)

mkdir ../cleaned;
mkdir ../after_sed;
mkdir ../final;

for f in "${FILES[@]}"
do
    >../cleaned/"$f"
    cat "$f" | while read line
    do
        echo "$line" | grep -E -v 'Invited Speaker|Colloquium Speakers|Staff|Institute Lecturers|Session Speakers|Organising Team' >> ../cleaned/"$f"
    done
done

for f in "${FILES[@]}"
do
    sed -r "s/\[short workshop\] |\[SHORT WORKSHOP\] |\[Short Workshop\] |\[Foundations\] |\[FOUNDATIONS\] |\[foundations\] //g" ../cleaned/"$f" > ../after_sed/"$f"
done

for f in "${FILES[@]}"
do
    sed -r 's/^[0-9]+. //g' ../after_sed/"$f" > ../final/"$f"
done

cd -
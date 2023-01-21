letterlist=("a b c d e f")

for i in $letterlist; do
    echo "/dev/sd$i"
    smartctl /dev/sd$i -a | grep "SMART overall-health self-assessment test result"
done


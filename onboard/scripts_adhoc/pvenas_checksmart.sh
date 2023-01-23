
for blockid in {a..f}; do
    echo "--------------------------------------"
    echo "/dev/sd${blockid}"
    smartctl /dev/sd${blockid} -a | grep "SMART overall-health self-assessment test result"
    smartctl --attributes /dev/sd${blockid}|grep -E "^ 12|^193"
done

#for blockid in {a..f}; do
#    echo ""
#    echo "sd${blockid}"
#    ./openSeaChest_Configure    --device /dev/sd${blockid} --puisFeature enable
#    ./openSeaChest_PowerControl --device /dev/sd${blockid} --powerBalanceFeature info
#done
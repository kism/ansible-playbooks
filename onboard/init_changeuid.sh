groupmod -g 1099 kgadmins

user=kism
uid=1089

echo $user
echo $uid

usermod  -u 1089 $user
groupmod -g 1089 $user

declare -a folders=("home" "srv" "opt" "etc" "media" "mnt")

## now loop through the above array
for i in "${arr[@]}"
do
   echo "$i"
   find "$i" -group $uid -exec chgrp -h $user {} \;
   find "$i" -user  $uid -exec chown -h $user {} \;
done
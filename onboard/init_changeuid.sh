groupmod -g 1099 kgadmins

user=ansible_svc
olduid=1000
newuid=1088

echo $user
echo $olduid
echo $newuid

usermod -u $newuid $user
groupmod -g $newuid $user

declare -a folders=("home" "srv" "opt" "etc" "media" "mnt")

find /srv -user  $olduid -exec chown  -h $user {} \;
find /srv -group $olduid -exec chgrp -h $user {} \;

find /home -user  $olduid -exec chown  -h $user {} \;
find /home -group $olduid -exec chgrp -h $user {} \;

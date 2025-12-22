#!/usr/bin/env bash

sudo apt-get -y install sshpass
export timestamp=$(date +%Y_%m_%d)

# backup database
pg_dump -h 127.0.0.1 -p 5432 -U admin -d cos > ~/cos.water_plant.${timestamp}.sql

# copy files
sshpass -p "linode4AnyLog!" ssh -o StrictHostKeyChecking=no root@50.116.20.125 "mkdir -p /root/sabetha/water_plant/${timestamp}"
sshpass -p "linode4AnyLog!" scp  -o StrictHostKeyChecking=no cos.water_plant.${timestamp}.sql  root@50.116.20.125:/root/sabetha/water_plant/${timestamp}

for year in `sudo ls /var/lib/docker/volumes/docker-compose-files_smart-city-operator1-data/_data/archive/` ; do
   for month in `sudo ls /var/lib/docker/volumes/docker-compose-files_smart-city-operator1-data/_data/archive/${year}` ; do
      for day in `sudo ls /var/lib/docker/volumes/docker-compose-files_smart-city-operator1-data/_data/archive/${year}/${month}` ; do
         echo "${year}/${month}/${day}"
         sudo sshpass -p "linode4AnyLog!" scp  -o StrictHostKeyChecking=no  scp /var/lib/docker/volumes/docker-compose-files_smart-city-operator1-data/_data/archive/${year}/${month}/${day}/cos.* root@50.116.20.125:/root/sabetha/water_plant/${timestamp}
      done
   done
done


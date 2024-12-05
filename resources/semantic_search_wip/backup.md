
### backup volumes

lerd@ipc615:/tmp$ sudo docker inspect elastic --format='{{json .Mounts}}'

(elastic container)
{"Type":"volume","Name":"elastic_esdata01","Source":"/var/lib/docker/volumes/elastic_esdata01/_data","Destination":"/usr/share/elasticsearch/data","Driver":"local","Mode":"rw","RW":true,"Propagation":""}

(elastic container)
{"Type":"volume","Name":"elastic_certs","Source":"/var/lib/docker/volumes/elastic_certs/_data","Destination":"/usr/share/elasticsearch/config/certs","Driver":"local","Mode":"rw","RW":true,"Propagation":""}

(kibana container)
[{"Type":"volume","Name":"elastic_kibanadata","Source":"/var/lib/docker/volumes/elastic_kibanadata/_data","Destination":"/usr/share/kibana/data","Driver":"local","Mode":"rw","RW":true,"Propagation":""},

{"Type":"volume","Name":"elastic_certs","Source":"/var/lib/docker/volumes/elastic_certs/_data","Destination":"/usr/share/kibana/config/certs","Driver":"local","Mode":"rw","RW":true,"Propagation":""}]

- backups the volume content into a tar.gz

```
sudo tar -czvf elastic_esdata01_backup.tar.gz -C /var/lib/docker/volumes/elastic_esdata01/_data .
sudo tar -czvf elastic_certs_backup.tar.gz -C /var/lib/docker/volumes/elastic_certs/_data .
sudo tar -czvf elastic_kibanadata_backup.tar.gz -C /var/lib/docker/volumes/elastic_kibanadata/_data .
```

### restore volumes

> maybe theres a mess with the prepended elastic, because it was like that from where we are coming
> maybe have to remove this prefix (or add it in the docker compose)

- recreate and repopulate the volumes (do for each)

```
docker volume create elastic_esdata01
sudo mkdir -p /var/lib/docker/volumes/elastic_esdata01/_data
sudo tar -xzvf elastic_esdata01_backup.tar.gz -C /var/lib/docker/volumes/elastic_esdata01/_data


```
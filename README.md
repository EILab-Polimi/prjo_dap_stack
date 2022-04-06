# First installation

Create the stack with it's volumes and services
Since we have installe docker compose V2 https://docs.docker.com/compose/cli-command/#install-on-linux

```
$ docker compose up -d --build
```

## drupal

> Just for the first time.

> Connect to :8080 port and install drupal

Then.

From the portainer console run the setup.sh for drupal
```
/opt/drupal# ./setup.sh
```

This will run composer require && drush enable modules

Sarebbe possibile copiare anche il custom module _dab_ nella `web/modules/custom`
ma dovremmo usare una repo a parte per il modulo

Per ora copiamo a mano il modulo _dab_ nel docker container

TODO trovare una soluzione per la gestione del modulo custom

## mosquitto

Copy the mosquitto.conf file in `mosquitto/conf`

TODO
Add a `Dockerfile` for mosquitto &&

set a `setup.sh` file like in drupal service and copy the `mosquitto.conf`

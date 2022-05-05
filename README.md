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

ATTENZIONE - se i paccheti da installare con composer sono già soddisfatti la compilazione non va a buon fine

Sarebbe possibile copiare anche il custom module _dab_ nella `web/modules/custom`
ma dovremmo usare una repo a parte per il modulo

Per ora copiamo a mano il modulo _dab_ nel docker container

TODO trovare una soluzione per la gestione del modulo custom

# PG admin
Utilizzato per importare i db
1. creare lo user
2. creare il dabase
3. Una volta creato il db vuoto con lo user corretto per reimportare il database selezionare il db right click e selezionare Restore. Il restore deve essere fatto passando un file ottenuto da un `pg_dump`
```
postgres@neo:~$ pg_dump -Fc prjo_dap_v2 > prjo_dap_v2.dump
```

# STACK first installation

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

## PG admin
Utilizzato per importare i db
1. creare lo user
2. creare il dabase
3. Una volta creato il db vuoto con lo user corretto per reimportare il database selezionare il db right click e selezionare Restore. Il restore deve essere fatto passando un file ottenuto da un `pg_dump`
```
postgres@neo:~$ pg_dump -Fc prjo_dap_v2 > prjo_dap_v2.dump
```

## qgis-server

Utiliziamo la versione qgis-server di camptocamp `https://hub.docker.com/r/camptocamp/qgis-server` specificando la versione 3.18

Scaricati i layer di esempio da `https://github.com/qgis/QGIS-Training-Data` (in Projecto) e copiato il contenuto della cartella `exercise_data/world` nella cartella `DAPStack/services/qgis-server/project` dell'host che è mappata sulla `/etc/qgisserver` del container come spiegato nella docker image

> Expects a `project.qgs` project file and all the files it depends on in the `/etc/qgisserver/` directory.

Ora si vede la mappa al
http://localhost:9003/?LAYERS=continents&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&CRS=EPSG:4326&WIDTH=400&HEIGHT=200&BBOX=-90,-180,90,180

Ho provato ad aggiungere la configurazione con `PGSERVICEFILE=/project/pg_service.conf` ed aggiungiunto il file `pg_service.conf` ma ancora non avevo connessione al server postgres in quanto puntava a `localhost` in vece che a `postgres`/`DAP_postgres`.

Invece, editando il file `waterPortfolio_v3.qgs` e modificando il nome dell'host a `DAP_postgres`
```
<layer-tree-layer legend_split_behavior="0" legend_exp="" checked="Qt::Checked" expanded="1" id="Wells_175ff862_8081_4abf_9e33_113ca68097d4" providerKey="postgres" patch_size="-1,-1" name="Wells" source="dbname='projecto' host=DAP_postgres port=5432 user='prjo' sslmode=disable key='id' srid=3004 type=PointZ checkPrimaryKeyUnicity='1' table=&quot;public&quot;.&quot;pozzi_attivi&quot; (geom)">
```

La connessione funziona ma poi ho errori relativi all'autenticazione dello user

# DAP

TODO
- Quando carichiamo la lista degli indicatori (route `/indicators` in fastAPI) ottengo una lista di `id_tabella_database`.

  Per creare il grafico ho bisogno, oltre che della tabella, anche della route per la visualizzazione di quell'indicatore (eg. i dati della tabella vengono visualizzati in 2 modi diversi -> 1! tabella 2 route)
  Quindi ci serve mappare oltre alla tabella anche la route

  Le route dei plot in fastapi devono essere
    - o mappate nel database con la relativa tabella
    - o normalizzate eg.
      `plot_def_drw_cycloM` e `plot_def_cycloM` sono le due route che usiamo per i primi due grafici degli indicatori. Entrambe effettuano una query alla stessa tabella `i_sqwdef_irrd_m` ma fanno elaborazioni->generano grafici differenti.

      Se le tabelle permettono di essere _elaborate_ tutte nello stesso modo allora _normaliziamo_ le route con nomi del tipo `/indicators/linear` o `/indicators/heatmap` ed aggiungiamo un select nella creazione del nuovo grafico

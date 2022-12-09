# prjo_dap_stack
Docker stack configuration for Decision Analytic Platform

# First installation

Create the stack with it's volumes and services
using docker compose V2 https://docs.docker.com/compose/cli-command/#install-on-linux

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

Post installation - contributed modules
```
 composer require 'drupal/bootstrap5:^2.0'
 composer require 'drupal/fontawesome:^2.24'
 composer require 'drupal/fontawesome_menu_icons:^1.9'
 composer require 'drupal/twig_tweak:^3.2'
```

# Services

- postgres - taken form postgres:14.1 image (https://hub.docker.com/layers/library/postgres/14.1/images/sha256-043c256b5dc621860539d8036d906eaaef1bdfa69a0344b4509b483205f14e63?context=explore) is used to host the drupal database, used for internal drupal functionality and the postgis extended prjo_dap database collecting the data used for graps and qgis projects data
- drupal - taken from drupal:9-apache image (https://hub.docker.com/layers/library/drupal/9-apache/images/sha256-4d6912ce1e909381212d88a8d478939b5e8701713624cc84c2ddad9af8a1feea?context=explore)
  which provide the web server and drupal CMS for the UCP platform.
- fastapi - starting from a python:3.8 image (https://hub.docker.com/layers/library/python/3.8/images/sha256-bb2a37b016b169c2d65f4203e15e855f77261353011810c18f2e6a080e2539e0?context=explore) we realized a fastAPI application (https://fastapi.tiangolo.com/) to serve graphs. The advantage to use fastAPI is we can browse and test the api results using the integrated swagger interfce (https://fastapi.tiangolo.com/features/#automatic-docs).
- qgis-server - taken from camptocamp/qgis-server:3.22 image (https://hub.docker.com/layers/camptocamp/qgis-server/3.22/images/sha256-76581170643935f0f53d4f59af4e25923d894c7e8c17c1ff702f0917a5cb33e9?context=explore)
implement a full qgis server version 3.22 (https://docs.qgis.org/3.22/en/docs/)

Additionally we have
- pgadmin4 service teaken from dpage/pgadmin4 image (https://hub.docker.com/r/dpage/pgadmin4) used for visually manage the postgresql database provided from the postgres service
- qgis-server-opengisch - taken from opengisch/qgis-server:3.26.2-focal image.

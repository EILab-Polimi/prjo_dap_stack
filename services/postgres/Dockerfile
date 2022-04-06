FROM postgres:14.1
RUN apt-get update \
    && apt-get install -y postgresql-14-postgis-3

# COPY ./services/postgres/setup/create_postgis_extension.sql /docker-entrypoint-initdb.d/
# COPY ./services/postgres/setup/drupal_user.sql /docker-entrypoint-initdb.d/
COPY ./services/postgres/setup/init-user-drupal.sh /docker-entrypoint-initdb.d/

FROM drupal:9-apache
RUN apt-get update && apt-get install -y git unzip
RUN ["/bin/bash", "-c", "composer self-update --2"]
RUN composer require --dev drush/drush

COPY ./services/drupal/setup /opt/drupal
# Change rights to setup bash script
RUN ["chmod", "+x", "/opt/drupal/setup.sh"]
# Running the script does not affect www/html directroy since we use volumes
RUN ["/opt/drupal/setup.sh"]

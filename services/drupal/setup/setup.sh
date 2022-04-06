#!/bin/sh
#set -e

echo "Running composer require"
# composer --version
# composer require drupal/group drupal/restui php-mqtt/client
composer require 'drupal/bootstrap5:^1.1'

# ./vendor/bin/drush en

# echo "Move dab module to modules/custom"

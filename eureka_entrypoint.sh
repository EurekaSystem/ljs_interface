#!/bin/bash

source "/opt/vulcanexus/$VULCANEXUS_DISTRO/setup.bash"
echo "source '/opt/vulcanexus/$VULCANEXUS_DISTRO/setup.bash'" >> ~/.bashrc

source "/app/install/setup.bash"
echo "source '/app/install/setup.bash'" >> ~/.bashrc

exec "$@"
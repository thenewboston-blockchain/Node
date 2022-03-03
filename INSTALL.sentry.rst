Deploy
======

This file describes how to deploy and setup a Sentry instance.

Description is based on https://github.com/getsentry/self-hosted

#. Provision at least 4Gb RAM and 40Gb disk Ubuntu Server 20.04 virtual machine.
#. Create DNS A record for `sentry.blockchain.thenewboston.com` to point to the virtual machine IP-address
#. Login to the virtual machine console::

    ssh ubuntu@sentry.blockchain.thenewboston.com  # for AWS EC2 instance

#. Add 16G swapfile::

    # Allocate swap space
    sudo -i
    fallocate -l 16G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile

    # Turn on swap file
    swapon /swapfile
    nano /etc/fstab
    # Add the following line
    # /swapfile swap swap defaults 0 0

    # Correcting swappiness
    sysctl vm.swappiness=10
    nano /etc/sysctl.conf
    # Add the following line
    # vm.swappiness=10

    reboot

    # Validate new settings
    swapon --show
    cat /proc/sys/vm/swappiness

#. Install prerequisites::

    sudo -i
    apt-get update
    apt-get install git nginx

#. Install Docker according to https://docs.docker.com/engine/install/ubuntu/
   (known working: Docker version 20.10.12, build e91ed57)

#. Install Docker Compose according to https://docs.docker.com/compose/install/
   (known working: docker-compose version 1.29.2, build 5becea4c)

#. Get the repository::

    sudo -i
    git clone https://github.com/getsentry/self-hosted.git
    cd self-hosted
    git checkout 22.2.0

#. Prepare configuration::

    # Copy `sentry.env.custom` from this repository
    scp node/config/settings/templates/sentry.env.custom ubuntu@sentry.blockchain.thenewboston.com:./self-hosted/.env.custom

#. Run installation::

    ./install.sh

#. Configure nginx::

    rm /etc/nginx/sites-enabled/default

    # Copy `sentry.nginx.conf` from this repository
    scp node/config/settings/templates/sentry.nginx.conf ubuntu@sentry.blockchain.thenewboston.com:/etc/nginx/sites-available/sentry.conf

    ln -s /etc/nginx/sites-available/sentry.conf /etc/nginx/sites-enabled/sentry.conf && \
    service nginx restart

#. Install and run certbot as described at https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal
   (Use "get and install your certificates" option)

#. Restart nginx::

    service nginx restart

#. Run Sentry::

    sudo -i
    docker-compose --env-file /root/self-hosted/.env.custom up -d

#. Check that Sentry is available at https://sentry.blockchain.thenewboston.com
#. Configure on "Welcome to Sentry" (keep defaults)

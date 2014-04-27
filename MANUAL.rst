=================================
How to setup your Bind server
=================================


Please note that in this document, *domain-name* is a reference to your fully qualified domain name. For example ``github.com``

- `Create a private key`_
- `Add your private key to the Bind configuration`_
- `Configure your zone to accept updates from key`_
- `Use nshome script to update your record`_
- `Troubleshooting`_

Create a private key
=======================

First, you will need to create a shared private key that will be used to communicate between the script and your server. Using `dnssec-keygen`__

.. __: http://ftp.isc.org/isc/bind9/cur/9.8/doc/arm/man.dnssec-keygen.html

In this example, I choose *hmac-sha256*, but this could be any of the following:  *hmac-md5, hmac-sha1, hmac-sha224, hmac-sha256, hmac-sha384 and hmac-sha512*

::

  dnssec-keygen -a hmac-sha256  -b 256 -n HOST domain-name.key

Here *domain-name* is the zone that allows dynamic updates, your domain name in most cases.

Next, grab the private key::

  perl -ne 'print if s/^Key: //' < Kdomain-name*.private


Add your private key to the Bind configuration
================================================

You'll need to enter this key in your Bind configuration file. I usually create a specific file for keys that is only readable by bind: ``/etc/bind/ddns.conf``

::

  # Note: the final dot in fqdn isn't mandatory here
  key domain-name {
        algorithm HMAC-SHA256;
        secret "KEY THAT WAS GRABED";
  };

Then ``chgrp /etc/bind/ddns.conf && chmod 0640 /etc/bind/ddns.conf`` to keep it *(relatively)* safe.


Configure your zone to accept updates from key
==================================================

Last step is to tell bind that it should accept DNS updates from your newly created key to update your domain. So, in your ``/etc/bind/named.conf.local``

::

  zone "domain-name" {
    type master;
    file "/etc/bind/db.domain-name";
    # your standard configuration …
    allow-update { key domain-name ; };
  };

Finally, reload bind using ``rndc reload`` and you should be set


Use nshome script to update your record
==============================================


You'll need both key files for nsupdate_ to work, any of them will work from the command line.

.. _nsupdate: http://ftp.isc.org/isc/bind9/cur/9.8/doc/arm/man.nsupdate.html

Assuming they're inside the same directory as the script, you can run is as this

::

  ./nshome.py -p5 -k Kdomain-name....key -n home.domain-name -s [your nameserver]

The script will run once and set the A record of home.domain-name to the "public" IP address of the machine where the script is run.

Then it will re-check the IP address every 5 minutes, and send a new update should the IP change.



Troubleshooting
==================

The main problem with dynamic updates is that when you wish to update your zone manually (to change something else), you'll need to *freeze* the zone first, and your db file will be messed up since Bind simply "dumps" the zone.

::

  rndc freeze domain-name
  # (edit your zone file)
  rndc reload domain-name
  rndc thaw domain-name

To avoid the problem of having a zone file messed up (and to avoid forgetting to freeze/thaw the zone), I usually create another zone dedicated to the record I wish to update, in the zone file::


  home IN NS [server-name]

Then create another *empty* db file ``db.sub.domain-name`` that Bind can mess up::

  @ IN SOA sub.domain-name admin.email. 2014042601 7200 7200 2419200 1200
  @ IN NS [server-name]


And another entry in your ``named.conf.local`` (you might wish to remove the *allow-update* from the upper zone)

::

  zone "home.domain-name" {
    type master;
    file "/etc/bind/db.home.domain-name";
    allow-update { key domain-name ; };
  };
  

=================================
How to setup your Bind server
=================================


Please note that in this document, *domain-name* is a reference to your fully qualified domain name. For example ``github.com``

- `Create a private key`_
- `Add the key to your zone`_
- `Configure your zone to accept updates from key`_
- `Use nshome script to update your record`_
- `Troubleshooting`_



Create a private key
=======================

First, you will need to create a private key that will be used to communicate between the script and your server. Using `ddns-confgen`__

.. __: https://bind.isc.org/doc/arm/9.11/man.ddns-confgen.html

::

  ddns-confgen -a hmac-sha384 -z domain-name

Here *domain-name* is the zone that allows dynamic updates. Your domain name in most cases.


Add the key to your server configuration
=====================================




Configure your zone to accept updates from key
==================================================

We should tell bind that it should accept DNS updates signed with that private key.

So, in your ``/etc/bind/named.conf.local``, first paste the output of the ddns-confgen tool

::

key "ddns-key.domain-name" {
  algorithm hmac-sha384;
  secret "xXxXxXxsx5XsxXXXXLT1sTFsv9roYdmmCmSI+opBkKEgt5131MW2mcIrszQXXXX";
};

  zone "domain-name" {
    type master;
    file "/etc/bind/db.domain-name";
    # your standard configuration …
    allow-update { key ddns-key.domain-name ; };
  };

Don't forget the **prefix** before your domain name if you added one. The *key* parameter here is the name of the record set in the zone (also, don't forget the final ``.``)

Finally, reload bind using ``rndc reload`` and you should be set

Use nshome script to update your record
==============================================

You'll need to save the output of the ddns-confgen tool to a "private" key file among with the nshome tool.

For example name it domain-name.key

Before trying to update your zone, be warned that Bind will probably mess up its contents when doing dynamic updates. To avoid that you can check out the `Troubleshooting`_ section and set up a child zone dedicated to the name you wish to use.

You'll need both key files for nsupdate_ to work, any of them will work from the command line.

.. _nsupdate: http://ftp.isc.org/isc/bind9/cur/9.11/doc/arm/man.nsupdate.html

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

  @     IN SOA sub.domain-name admin.email. 2014042601 7200 7200 2419200 1200
  @     IN NS [server-name]
  _key  IN KEY … 


And another entry in your ``named.conf.local`` (you might wish to remove the *allow-update* from the upper zone)

::

  zone "home.domain-name" {
    type master;
    file "/etc/bind/db.home.domain-name";
    allow-update { key _key.home.domain-name ; };
  };
  

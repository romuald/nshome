nshome
======

This script may be used by people having a "dynamic IP" ISP and administrating their own DNS server.

It sends a dynamic update to update a specific record within your DNS zone (using Bind nsupdate_ binary)

.. _nsupdate: http://ftp.isc.org/isc/bind9/cur/9.8/doc/arm/man.nsupdate.html


Sample usage::

  nshome -k Khome.example.com.private -n home.example.com  -s ns.example.com

This will send an update to *ns.example.com* to overwrite *home.example.com* to your current IP address.

It assumes the zone is correctly configured on the server part to accept updates to *example.com* with the *home.examplecom.private* key

You can add the ``-p5`` option to check for IP every 5 minutes and only send update if it changed


You might wish to checkout the `<MANUAL.rst>`_ file to see how to set up your DNS server


Since the script needs the nsupdate_ binary, you'll need to install it:

- Debian/Ubuntu: ``apt-get install dnsutils bind9utils``
- MacOS: ``brew install bind``



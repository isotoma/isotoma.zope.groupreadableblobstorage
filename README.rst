isotoma.zope.groupreadableblobstorage
=====================================

This is a packaged version of a monkey patch to allow group-readable
blobstorage as found here:

http://stackoverflow.com/questions/6168566/collective-xsendfile-zodb-blobs-and-unix-file-permissions

It is modified from the original posting by Martijn Pieters as initial testing
sugested the patch was happening too late.

Using with zope
---------------

Adding this egg to your zope instance is enough to apply the monkey patch - it
advertises it's self using the z3c.autoinclude plugin mechanism and will be
loaded as the ZCML is loaded::

    [instance]
    eggs =
        isotoma.zope.groupreadableblobstorage


Using with zeo
--------------

To use this with a zeoserver, you need to add an ``%import
isotoma.zope.groupreadableblobstorage`` to your zeo.conf.

If you are using plone.recipe.zeoserver you can do this::

    [zeoserver]
    eggs = isotoma.zope.groupreadableblobstorage
    zeo-conf-additional =
        %import isotoma.zope.groupreadableblobstorage

Note that this form hasn't beed tested.

If you are using isotoma.recipe.zeo you can do this::

    [zeoserver]
    eggs = isotoma.zope.groupreadableblobstorage
    import = isotoma.zope.groupreadableblobstorage


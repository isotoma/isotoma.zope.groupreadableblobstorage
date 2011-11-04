"""
Monkey patch the blobstorage to do 750 permisions - modified from 
http://stackoverflow.com/questions/6168566/collective-xsendfile-zodb-blobs-and-unix-file-permissions
"""

import os
from ZODB import utils
from ZODB.blob import FilesystemHelper
from ZODB.blob import log, LAYOUT_MARKER

def create(self):
    if not os.path.exists(self.base_dir):
        os.makedirs(self.base_dir, 0750)
        log("Blob directory '%s' does not exist. "
            "Created new directory." % self.base_dir)
    if not os.path.exists(self.temp_dir):
        os.makedirs(self.temp_dir, 0750)
        log("Blob temporary directory '%s' does not exist. "
            "Created new directory." % self.temp_dir)

    if not os.path.exists(os.path.join(self.base_dir, LAYOUT_MARKER)):
        layout_marker = open(
            os.path.join(self.base_dir, LAYOUT_MARKER), 'wb')
        layout_marker.write(self.layout_name)
    else:
        layout = open(os.path.join(self.base_dir, LAYOUT_MARKER), 'rb'
                      ).read().strip()
        if layout != self.layout_name:
            raise ValueError(
                "Directory layout `%s` selected for blob directory %s, but "
                "marker found for layout `%s`" %
                (self.layout_name, self.base_dir, layout))

def isSecure(self, path):
    """Ensure that (POSIX) path mode bits are 0750."""
    return (os.stat(path).st_mode & 027) == 0

def getPathForOID(self, oid, create=False):
    """Given an OID, return the path on the filesystem where
    the blob data relating to that OID is stored.

    If the create flag is given, the path is also created if it didn't
    exist already.

    """
    # OIDs are numbers and sometimes passed around as integers. For our
    # computations we rely on the 64-bit packed string representation.
    if isinstance(oid, int):
        oid = utils.p64(oid)

    path = self.layout.oid_to_path(oid)
    path = os.path.join(self.base_dir, path)

    if create and not os.path.exists(path):
        try:
            os.makedirs(path, 0750)
        except OSError:
            # We might have lost a race.  If so, the directory
            # must exist now
            assert os.path.exists(path)
    return path

FilesystemHelper.create = create
FilesystemHelper.isSecure = isSecure
FilesystemHelper.getPathForOID = getPathForOID


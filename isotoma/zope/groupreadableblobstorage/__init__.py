"""
Monkey patch the blobstorage to do 750 permisions - modified from 
http://stackoverflow.com/questions/6168566/collective-xsendfile-zodb-blobs-and-unix-file-permissions
"""

import os
import tempfile
import weakref

from ZODB import utils
from ZODB.blob import FilesystemHelper, BlobStorageMixin, Blob, is_blob_record
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

def blob_mkstemp(self, oid, tid):
    """Given an oid and a tid, return a temporary file descriptor
    and a related filename.

    The file is guaranteed to exist on the same partition as committed
    data, which is important for being able to rename the file without a
    copy operation.  The directory in which the file will be placed, which
    is the return value of self.getPathForOID(oid), must exist before this
    method may be called successfully.
    """
    oidpath = self.getPathForOID(oid)
    fd, name = tempfile.mkstemp(suffix='.tmp', prefix=utils.tid_repr(tid),
                                dir=oidpath)
    os.chmod(name, 0640)
    return fd, name

FilesystemHelper.create = create
FilesystemHelper.isSecure = isSecure
FilesystemHelper.getPathForOID = getPathForOID
FilesystemHelper.blob_mkstemp = blob_mkstemp



def copyTransactionsFrom(self, other):
    for trans in other.iterator():
        self.tpc_begin(trans, trans.tid, trans.status)
        for record in trans:
            blobfilename = None
            if is_blob_record(record.data):
                try:
                    blobfilename = other.loadBlob(record.oid, record.tid)
                except POSKeyError:
                    pass
            if blobfilename is not None:
                fd, name = tempfile.mkstemp(
                    suffix='.tmp', dir=self.fshelper.temp_dir)
                os.close(fd)
                os.chmod(name, 0640)
                utils.cp(open(blobfilename, 'rb'), open(name, 'wb'))
                self.restoreBlob(record.oid, record.tid, record.data,
                                 name, record.data_txn, trans)
            else:
                self.restore(record.oid, record.tid, record.data,
                             '', record.data_txn, trans)

        self.tpc_vote(trans)
        self.tpc_finish(trans)

BlobStorageMixin.copyTransactionsFrom = copyTransactionsFrom




def _create_uncommitted_file(self):
    assert self._p_blob_uncommitted is None, (
        "Uncommitted file already exists.")
    if self._p_jar:
        tempdir = self._p_jar.db()._storage.temporaryDirectory()
    else:
        tempdir = tempfile.gettempdir()
    filename = utils.mktemp(dir=tempdir)
    os.chmod(filename, 0640)
    self._p_blob_uncommitted = filename

    def cleanup(ref):
        if os.path.exists(filename):
            os.remove(filename)

    self._p_blob_ref = weakref.ref(self, cleanup)
    return filename

Blob._create_uncommitted_file = _create_uncommitted_file


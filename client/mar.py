"""%prog [options] -t|-s marfile

Utility for managing mar file

Author: Mihai Tabara (adaptation of Chris Atlee's mar.py implementation)
"""

import struct
import os
import hashlib


def packint(i):
    return struct.pack(">L", i)


def unpackint(s):
    return struct.unpack(">L", s)[0]


class MarInfo:
    """Represents information about a member of a MAR file. The following
    attributes are supported:
        `size`:     the file's size
        `name`:     the file's name
        `flags`:    file permission flags
        `_offset`:  where in the MAR file this member exists
    """
    size = None
    name = None
    flags = None
    _offset = None

    # The member info is serialized as a sequence of 4-byte integers
    # representing the offset, size, and flags of the file followed by a null
    # terminated string representing the filename
    _member_fmt = ">LLL"

    @classmethod
    def from_fileobj(cls, fp):
        """Return a MarInfo object by reading open file object `fp`"""
        self = cls()
        data = fp.read(12)
        if not data:
            # EOF
            return None
        if len(data) != 12:
            raise ValueError("Malformed mar?")
        self._offset, self.size, self.flags = struct.unpack(
            cls._member_fmt, data)
        name = ""
        while True:
            c = fp.read(1)
            if c is None:
                raise ValueError("Malformed mar?")
            if c == "\x00":
                break
            name += c
        self.name = name
        return self

    def __repr__(self):
        return "<%s %o %s bytes starting at %i>" % (
            self.name, self.flags, self.size, self._offset)

    def to_bytes(self):
        return struct.pack(self._member_fmt, self._offset, self.size, self.flags) + \
            self.name + "\x00"


class MarFile:
    """Represents a MAR file on disk.

    `name`:     filename of MAR file
    `mode`:     either 'r' or 'w', depending on if you're reading or writing.
                defaults to 'r'
    """
    _longint_fmt = ">L"

    def __init__(self, name, mode="r"):
        if mode not in "r":
            raise ValueError("Mode must be 'r'")

        self.name = name
        self.mode = mode
        self.fileobj = open(name, 'rb')

        # hash digest of the members, it excludes the signature
        self.digest = hashlib.sha512()

        self.members = []

        # Current offset of our index in the file. This gets updated as we add
        # files to the MAR. This also refers to the end of the file until we've
        # actually written the index
        self.index_offset = 8

        # Flag to indicate that we need to re-write the index
        self.rewrite_index = False

        # Read the file's index and compute hash
        self._read_index()

        # Compute the hash of its members
        self._compute_hash()

    def _read_index(self):
        fp = self.fileobj
        fp.seek(0)
        # Read the header
        header = fp.read(8)
        magic, self.index_offset = struct.unpack(">4sL", header)
        if magic != "MAR1":
            raise ValueError("Bad magic")
        fp.seek(self.index_offset)

        # Read the index_size, we don't use it though
        # We just read all the info sections from here to the end of the file
        fp.read(4)

        self.members = []

        while True:
            info = MarInfo.from_fileobj(fp)
            if not info:
                break
            self.members.append(info)

        # Sort them by where they are in the file
        self.members.sort(key=lambda info: info._offset)

        # Read any signatures
        first_offset = self.members[0]._offset
        signature_offset = 16
        if signature_offset < first_offset:
            fp.seek(signature_offset)
            # do nothing with the signatures - just consume the data
            unpackint(fp.read(4))

    def _compute_hash(self):
        with open(self.name, 'rb') as digestfp:
            digestfp.seek(0)

            for member in self.members:
                digestfp.seek(member._offset)
                data = digestfp.read(member.size)
                self.digest.update(data)

    def __del__(self):
        """Close the file when we're garbage collected"""
        if self.fileobj:
            self.fileobj.close()
            self.fileobj = None


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(__doc__)
    parser.set_defaults(
        action=None,
    )
    parser.add_option("-t", "--list", action="store_const", const="list",
                      dest="action", help="print out MAR contents")
    parser.add_option("-s", "--hash", action="store_const", const="hash",
                      dest="action", help="hash of the contents of the file")

    options, args = parser.parse_args()

    if not options.action:
        parser.error("Must specify something to do (one of -t, -s)")

    if not args:
        parser.error("You must specify at least a marfile to work with")

    marfile = args[0]
    marfile = os.path.abspath(marfile)

    mar_class = MarFile

    if options.action == "list":
        m = mar_class(marfile)
        print "%-7s %-7s %-7s" % ("SIZE", "MODE", "NAME")
        for m in m.members:
            print "%-7i %04o    %s" % (m.size, m.flags, m.name)

    elif options.action == "hash":
        m = mar_class(marfile)
        print m.digest.hexdigest()

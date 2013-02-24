import binascii
import logging
import struct


SERVER_NAME = '0000'


# struct format strings for parsing buffer lengths
# don't forget, you have to pad a 3-byte value with \x00
_SIZE_FORMATS = ['!B', '!H', '!I', '!I']


def parse_variable_array(buf, lenbytes):
    """
    Parse an array described using the 'Type name<x..y>' syntax from the spec

    Read a length at the start of buf, and returns that many bytes
    after, in a tuple with the TOTAL bytes consumed (including the size). This
    does not check that the array is the right length for any given datatype.
    """
    # first have to figure out how to parse length
    assert lenbytes <= 4  # pretty sure 4 is impossible, too
    size_format = _SIZE_FORMATS[lenbytes - 1]
    padding = '\x00' if lenbytes == 3 else ''
    # read off the length
    size = struct.unpack(size_format, padding + buf[:lenbytes])[0]
    # read the actual data
    data = buf[lenbytes:lenbytes + size]
    # if len(data) != size: insufficient data
    return data, size + lenbytes


def parse_opaque(data, lenbytes=2):
    """
    Parses an opaque structure of TLS and returns the number of bytes
    consumed (length of the opaque structure + lenbytes).
    @param lenbytes: how many bytes encode the length
    """
    if len(data) < lenbytes:
        raise ValueError("data too short: len(data)=%d" % (len(data),))
    try:
        opaqlen = 0
        for lenbyte in range(0, lenbytes):
            opaqlen += struct.unpack('B', data[lenbyte])[0] * (2 ** ((lenbytes - lenbyte - 1) * 8))
        return data[lenbytes:lenbytes + opaqlen], opaqlen + lenbytes
    except Exception:
        import traceback
        traceback.print_exc()
        raise


class ClientHello(object):

    def __init__(self, data):
        logging.debug('parsing clienthello with length %d bytes' % len(data))
        self.tcp_header = None
        self.handshake_header = None
        self.version = None
        self.random = None
        self.session_id = None
        self.cipher_suites = None
        self.compression_support = None
        self.extensions = {}
        # parse data
        self.__parse(data)

    def __parse(self, data):
        # read static fields
        self.tcp_header = binascii.hexlify(data[0:5])
        self.handshake_header = binascii.hexlify(data[5:9])
        self.version = binascii.hexlify(data[9:11])
        self.random = binascii.hexlify(data[11:43])

        # read dynamic length fields moving pointer
        ptr = 43

        session_id, offset = parse_variable_array(data[ptr:], 1)
        self.session_id = binascii.hexlify(session_id)
        ptr += offset

        cipher_suites, offset = parse_variable_array(data[ptr:], 2)
        self.cipher_suites = binascii.hexlify(cipher_suites)
        ptr += offset

        compression_support, offset = parse_variable_array(data[ptr:], 1)
        self.compression_support = binascii.hexlify(compression_support)
        ptr += offset

        # test if it's a extended client hello with tls extensions defined
        if len(data[ptr:]) > 2:
            extension_list, offset = parse_variable_array(data[ptr:], 2)
            ptr = 0
            while ptr < len(extension_list):
                extension_type = binascii.hexlify(extension_list[ptr:ptr+2])
                ptr += 2
                extension_value, offset = parse_opaque(extension_list[ptr:], 2)
                ptr += offset
                self.extensions[extension_type] = extension_value

    def get_server_name(self):
        """
        As server_name is a list of names prefixed with the type, we have to parse the
        host_name(0) type. @see: http://www.ietf.org/rfc/rfc3546.txt Page 8
        """
        server_name_list = self.extensions.get(SERVER_NAME, None)
        if server_name_list is not None:
            ptr = 0
            server_list, offset = parse_variable_array(server_name_list[ptr:], 2)
            ptr += 2
            while ptr < len(server_name_list):
                name_type = binascii.hexlify(server_name_list[ptr:ptr+1])
                ptr += 1
                if name_type == '00':  # this is the host_name type
                    host_name, offset = parse_opaque(server_name_list[ptr:], 2)
                    ptr += offset
                    return host_name
        return None


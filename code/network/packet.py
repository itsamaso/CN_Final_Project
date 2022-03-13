import struct

from . import keys, constants

TYPE_SESSION_REQUEST = 1
TYPE_SESSION_COOKIE = 2
TYPE_SESSION_PRESERVE = 4
TYPE_USERS_REQUEST = 5
TYPE_USERS_RESPONSE = 6
TYPE_USER_DATA_REQUEST = 7
TYPE_USER_DATA_RESPONSE = 8
TYPE_MESSAGE_REQUEST = 9
TYPE_MESSAGE_RESPONSE = 10
TYPE_BROADCAST_REQUEST = 11
TYPE_BROADCAST_RESPONSE = 12
TYPE_INCOMING_MESSAGE_REQUEST = 13
TYPE_INCOMING_MESSAGE_RESPONSE = 14
TYPE_FILES_REQUEST = 15
TYPE_FILES_RESPONSE = 16
TYPE_FILE_DATA_REQUEST = 17
TYPE_FILE_DATA_RESPONSE = 18
TYPE_FILE_DOWNLOAD_REQUEST = 19
TYPE_FILE_DOWNLOAD_RESPONSE = 20
TYPE_DOWNLOAD_CHUNK_REQUEST = 21
TYPE_DOWNLOAD_CHUNK_RESPONSE = 22
TYPE_FILE_UPLOAD_REQUEST = 23
TYPE_FILE_UPLOAD_RESPONSE = 24
TYPE_UPLOAD_CHUNK_REQUEST = 25
TYPE_UPLOAD_CHUNK_RESPONSE = 26

SIZE_TYPE = 2

FORMAT_BLOB = '{}s'
FORMAT_PACKET_TYPE = '!H'
FORMAT_SESSION_REQUEST = '!HH{}'
FORMAT_SESSION_COOKIE = '!HQQ'
FORMAT_SESSION_PRESERVE = '!HQ'
FORMAT_USERS_REQUEST = '!HQ'
FORMAT_USERS_RESPONSE = '!HH{}'
FORMAT_USER_DATA_REQUEST = '!HQQ'
FORMAT_USER_DATA_RESPONSE = '!HQH{}'
FORMAT_MESSAGE_REQUEST = '!HQQQH{}'
FORMAT_MESSAGE_RESPONSE = '!HQ'
FORMAT_BROADCAST_REQUEST = '!HQQH{}'
FORMAT_BROADCAST_RESPONSE = '!HQ'
FORMAT_INCOMING_MESSAGE_REQUEST = '!HQQH{}'
FORMAT_INCOMING_MESSAGE_RESPONSE = '!HQ'
FORMAT_FILES_REQUEST = '!HQ'
FORMAT_FILES_RESPONSE = '!HH{}'
FORMAT_FILE_DATA_REQUEST = '!HQQ'
FORMAT_FILE_DATA_RESPONSE = '!HQLH{}'
FORMAT_FILE_DOWNLOAD_REQUEST = '!HQQ'
FORMAT_FILE_DOWNLOAD_RESPONSE = '!HQQ'
FORMAT_DOWNLOAD_CHUNK_REQUEST = '!HQL'
FORMAT_DOWNLOAD_CHUNK_RESPONSE = '!HQLH{}'
FORMAT_FILE_UPLOAD_REQUEST = '!HQLH{}'
FORMAT_FILE_UPLOAD_RESPONSE = '!HQQ'
FORMAT_UPLOAD_CHUNK_REQUEST = '!HQLH{}'
FORMAT_UPLOAD_CHUNK_RESPONSE = '!HQL'

# method for getting the type of a packet
def get_type(data):

    chunk_type = data[0:SIZE_TYPE]
    pieces = struct.unpack(FORMAT_PACKET_TYPE, chunk_type)

    packet_type = pieces[0]

    return packet_type

    ############################################################
    # GENERATORS FOR PACKETS                                   #
    ############################################################

# method for generating packet of type "SESSION REQUEST"
def generate_session_request(**arguments):

    name_user = arguments[keys.NAME_USER]

    name_user_blob = bytes(name_user, encoding='UTF-8')
    name_user_length = len(name_user_blob)
    name_user_format = FORMAT_BLOB.format(name_user_length)

    packet_format = FORMAT_SESSION_REQUEST.format(name_user_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_SESSION_REQUEST,
        name_user_length,
        name_user_blob,
    )

    return blob_packet

# method for generating packet of type "SESSION COOKIE"
def generate_session_cookie(**arguments):

    number_user = arguments[keys.NUMBER_USER]
    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_SESSION_COOKIE

    blob_packet = struct.pack(
        packet_format,
        TYPE_SESSION_COOKIE,
        number_user,
        number_session,
    )

    return blob_packet

# method for generating packet of type "SESSION PRESERVE"
def generate_session_preserve(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_SESSION_PRESERVE

    blob_packet = struct.pack(
        packet_format,
        TYPE_SESSION_PRESERVE,
        number_session,
    )

    return blob_packet

# method for generating packet of type "USERS REQUEST"
def generate_users_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_USERS_REQUEST

    blob_packet = struct.pack(
        packet_format,
        TYPE_USERS_REQUEST,
        number_session,
    )

    return blob_packet

# method for generating packet of type "USERS RESPONSE"
def generate_users_response(**arguments):

    list_numbers_users = arguments[keys.LIST_NUMBERS_USERS]

    numbers_users_length = len(list_numbers_users)
    numbers_users_format = 'Q' * numbers_users_length

    packet_format = FORMAT_USERS_RESPONSE.format(numbers_users_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_USERS_RESPONSE,
        numbers_users_length,
        *list_numbers_users,
    )

    return blob_packet

# method for generating packet of type "USER DATA REQUEST"
def generate_user_data_request(**arguments):

    number_user = arguments[keys.NUMBER_USER]
    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_USER_DATA_REQUEST

    blob_packet = struct.pack(
        packet_format,
        TYPE_USER_DATA_REQUEST,
        number_session,
        number_user,
    )
    
    return blob_packet

# method for generating packet of type "USER DATA RESPONSE"
def generate_user_data_response(**arguments):

    number_user = arguments[keys.NUMBER_USER]
    name_user = arguments[keys.NAME_USER]

    name_user_blob = bytes(name_user, encoding='UTF-8')
    name_user_length = len(name_user_blob)
    name_user_format = FORMAT_BLOB.format(name_user_length)

    packet_format = FORMAT_USER_DATA_RESPONSE.format(name_user_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_USER_DATA_RESPONSE,
        number_user,
        name_user_length,
        name_user_blob,
    )

    return blob_packet

# method for generating packet of type "MESSAGE REQUEST"
def generate_message_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]
    number_user = arguments[keys.NUMBER_USER]
    number_message = arguments[keys.NUMBER_MESSAGE]
    message = arguments[keys.MESSAGE]

    message_blob = bytes(message, encoding='UTF-8')
    length_message_blob = len(message_blob)
    format_message_blob = FORMAT_BLOB.format(length_message_blob)

    packet_format = FORMAT_MESSAGE_REQUEST.format(format_message_blob)

    blob_packet = struct.pack(
        packet_format,
        TYPE_MESSAGE_REQUEST,
        number_session,
        number_user,
        number_message,
        length_message_blob,
        message_blob,
    )

    return blob_packet

# method for generating packet of type "MESSAGE RESPONSE"
def generate_message_response(**arguments):

    number_message = arguments[keys.NUMBER_MESSAGE]

    packet_format = FORMAT_MESSAGE_RESPONSE

    blob_packet = struct.pack(
        packet_format,
        TYPE_MESSAGE_RESPONSE,
        number_message,
    )

    return blob_packet

# method for generating packet of type "BROADCAST REQUEST"
def generate_broadcast_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]
    number_message = arguments[keys.NUMBER_MESSAGE]
    message = arguments[keys.MESSAGE]

    message_blob = bytes(message, encoding='UTF-8')
    length_message_blob = len(message_blob)
    format_message_blob = FORMAT_BLOB.format(length_message_blob)

    packet_format = FORMAT_BROADCAST_REQUEST.format(format_message_blob)

    blob_packet = struct.pack(
        packet_format,
        TYPE_BROADCAST_REQUEST,
        number_session,
        number_message,
        length_message_blob,
        message_blob,
    )

    return blob_packet

# method for generating packet of type "BROADCAST RESPONSE"
def generate_broadcast_response(**arguments):

    number_message = arguments[keys.NUMBER_MESSAGE]

    packet_format = FORMAT_BROADCAST_RESPONSE

    blob_packet = struct.pack(
        packet_format,
        TYPE_BROADCAST_RESPONSE,
        number_message,
    )

    return blob_packet

# method for generating packet of type "INCOMING MESSAGE REQUEST"
def generate_incoming_message_request(**arguments):

    number_user = arguments[keys.NUMBER_USER]
    number_message = arguments[keys.NUMBER_MESSAGE]
    message = arguments[keys.MESSAGE]

    message_blob = bytes(message, encoding='UTF-8')

    length_message_blob = len(message_blob)
    format_message_blob = FORMAT_BLOB.format(length_message_blob)

    packet_format = FORMAT_INCOMING_MESSAGE_REQUEST.format(format_message_blob)

    packet_blob = struct.pack(
        packet_format,
        TYPE_INCOMING_MESSAGE_REQUEST,
        number_user,
        number_message,
        length_message_blob,
        message_blob,
    )

    return packet_blob

# method for generating packet of type "INCOMING MESSAGE RESPONSE"
def generate_incoming_message_response(**arguments):

    number_message = arguments[keys.NUMBER_MESSAGE]

    packet_format = FORMAT_INCOMING_MESSAGE_RESPONSE

    packet_blob = struct.pack(
        packet_format,
        TYPE_INCOMING_MESSAGE_RESPONSE,
        number_message,
    )

    return packet_blob

# method for generating packet of type "FILES REQUEST"
def generate_files_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_FILES_REQUEST

    packet_blob = struct.pack(
        packet_format,
        TYPE_FILES_REQUEST,
        number_session,
    )

    return packet_blob

# method for generating packet of type "FILES RESPONSE"
def generate_files_response(**arguments):

    list_numbers_files = arguments[keys.LIST_NUMBERS_FILES]

    numbers_files_length = len(list_numbers_files)
    numbers_files_format = 'Q' * numbers_files_length

    packet_format = FORMAT_FILES_RESPONSE.format(numbers_files_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_FILES_RESPONSE,
        numbers_files_length,
        *list_numbers_files,
    )

    return blob_packet

# method for generating packet of type "FILE DATA REQUEST"
def generate_file_data_request(**arguments):

    number_file_server = arguments[keys.NUMBER_FILE_SERVER]
    number_session = arguments[keys.NUMBER_SESSION]

    packet_format = FORMAT_FILE_DATA_REQUEST

    blob_packet = struct.pack(
        packet_format,
        TYPE_FILE_DATA_REQUEST,
        number_session,
        number_file_server,
    )

    return blob_packet

# method for generating packet of type "FILE DATA RESPONSE"
def generate_file_data_response(**arguments):

    number_file_server = arguments[keys.NUMBER_FILE_SERVER]
    name_file = arguments[keys.NAME_FILE]
    size_file = arguments[keys.SIZE_FILE]

    name_file_blob = bytes(name_file, encoding='UTF-8')
    name_file_length = len(name_file_blob)
    name_file_format = FORMAT_BLOB.format(name_file_length)

    packet_format = FORMAT_FILE_DATA_RESPONSE.format(name_file_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_FILE_DATA_RESPONSE,
        number_file_server,
        size_file,
        name_file_length,
        name_file_blob,
    )

    return blob_packet

# method for generating packet of type "FILE DOWNLOAD REQUEST"
def generate_file_download_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]
    number_file_server = arguments[keys.NUMBER_FILE_SERVER]

    packet_format = FORMAT_FILE_DOWNLOAD_REQUEST

    blob_packet = struct.pack(
        packet_format,
        TYPE_FILE_DOWNLOAD_REQUEST,
        number_session,
        number_file_server,
    )

    return blob_packet

# method for generating packet of type "FILE DOWNLOAD RESPONSE"
def generate_file_download_response(**arguments):

    number_file_server = arguments[keys.NUMBER_FILE_SERVER]
    transaction_download = arguments[keys.TRANSACTION_DOWNLOAD]

    packet_format = FORMAT_FILE_DOWNLOAD_RESPONSE

    blob_packet = struct.pack(
        packet_format,
        TYPE_FILE_DOWNLOAD_RESPONSE,
        number_file_server,
        transaction_download,
    )

    return blob_packet

# method for generating packet of type "DOWNLOAD CHUNK REQUEST"
def generate_download_chunk_request(**arguments):

    transaction_download = arguments[keys.TRANSACTION_DOWNLOAD]
    number_chunk = arguments[keys.NUMBER_CHUNK]

    packet_format = FORMAT_DOWNLOAD_CHUNK_REQUEST

    blob_packet = struct.pack(
        packet_format,
        TYPE_DOWNLOAD_CHUNK_REQUEST,
        transaction_download,
        number_chunk,
    )

    return blob_packet

# method for generating packet of type "DOWNLOAD CHUNK RESPONSE"
def generate_download_chunk_response(**arguments):

    transaction_download = arguments[keys.TRANSACTION_DOWNLOAD]
    number_chunk = arguments[keys.NUMBER_CHUNK]
    blob_chunk = arguments[keys.BLOB_CHUNK]

    blob_chunk_length = len(blob_chunk)
    blob_chunk_format = FORMAT_BLOB.format(blob_chunk_length)

    packet_format = FORMAT_DOWNLOAD_CHUNK_RESPONSE.format(blob_chunk_format)

    blob_packet = struct.pack(
        packet_format,
        TYPE_DOWNLOAD_CHUNK_RESPONSE,
        transaction_download,
        number_chunk,
        blob_chunk_length,
        blob_chunk,
    )

    return blob_packet

# method for generating packet of type "FILE UPLOOAD REQUEST"
def generate_file_upload_request(**arguments):

    number_session = arguments[keys.NUMBER_SESSION]
    size_file = arguments[keys.SIZE_FILE]
    name_file = arguments[keys.NAME_FILE]

    blob_name_file = bytes(name_file, encoding='UTF-8')
    length_name_file = len(blob_name_file)
    format_name_file = FORMAT_BLOB.format(length_name_file)

    packet_format = FORMAT_FILE_UPLOAD_REQUEST.format(format_name_file)

    packet_blob = struct.pack(
        packet_format,
        TYPE_FILE_UPLOAD_REQUEST,
        number_session,
        size_file,
        length_name_file,
        blob_name_file,
    )

    return packet_blob

# method for generating packet of type "FILE UPLOAD RESPONSE"
def generate_file_upload_response(**arguments):

    number_file_server = arguments[keys.NUMBER_FILE_SERVER]
    transaction_upload = arguments[keys.TRANSACTION_UPLOAD]

    packet_format = FORMAT_FILE_UPLOAD_RESPONSE

    packet_blob = struct.pack(
        packet_format,
        TYPE_FILE_UPLOAD_RESPONSE,
        number_file_server,
        transaction_upload,
    )

    return packet_blob

# method for generating packet of type "UPLOAD CHUNK REQUEST"
def generate_upload_chunk_request(**arguments):

    transaction_upload = arguments[keys.TRANSACTION_UPLOAD]
    number_chunk = arguments[keys.NUMBER_CHUNK]
    blob_chunk = arguments[keys.BLOB_CHUNK]

    length_blob_chunk = len(blob_chunk)
    format_blob_chunk = FORMAT_BLOB.format(length_blob_chunk)

    packet_format = FORMAT_UPLOAD_CHUNK_REQUEST.format(format_blob_chunk)

    packet_blob = struct.pack(
        packet_format,
        TYPE_UPLOAD_CHUNK_REQUEST,
        transaction_upload,
        number_chunk,
        length_blob_chunk,
        blob_chunk,
    )

    return packet_blob

# method for generating packet of type "UPLOAD CHUNK RESPONSE"
def generate_upload_chunk_response(**arguments):

    transaction_upload = arguments[keys.TRANSACTION_UPLOAD]
    number_chunk = arguments[keys.NUMBER_CHUNK]

    packet_format = FORMAT_UPLOAD_CHUNK_RESPONSE

    packet_blob = struct.pack(
        packet_format,
        TYPE_UPLOAD_CHUNK_RESPONSE,
        transaction_upload,
        number_chunk,
    )

    return packet_blob

    ############################################################
    # PARSERS FOR PACKETS                                      #
    ############################################################

# parser for packet of type "SESSION REQUEST"
def parse_session_request(data):

    header_format = FORMAT_SESSION_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    name_user_length = pieces[1]
    name_user_format = FORMAT_BLOB.format(name_user_length)

    packet_format = FORMAT_SESSION_REQUEST.format(name_user_format)

    pieces = struct.unpack(packet_format, data)

    name_user = str(pieces[2], encoding='UTF-8')

    variables = {
        keys.NAME_USER: name_user,
    }

    return variables

# parser for packet of type "SESSION COOKIE"
def parse_session_cookie(data):

    packet_format = FORMAT_SESSION_COOKIE

    pieces = struct.unpack(packet_format, data)

    number_user = pieces[1]
    number_session = pieces[2]

    session_data = {
        keys.NUMBER_USER: number_user,
        keys.NUMBER_SESSION: number_session,
    }

    return session_data

# parser for packet of type "SESSION PRESERVE"
def parse_session_preserve(data):

    packet_format = FORMAT_SESSION_PRESERVE

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]

    session_data = {
        keys.NUMBER_SESSION: number_session,
    }

    return session_data

# parser for packet of type "USERS REQUEST"
def parse_users_request(data):

    packet_format = FORMAT_USERS_REQUEST

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]

    session_data = {
        keys.NUMBER_SESSION: number_session,
    }

    return session_data

# parser for packet of type "USERS RESPONSE"
def parse_users_response(data):

    header_format = FORMAT_USERS_RESPONSE.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    numbers_users_length = pieces[1]
    numbers_users_format = 'Q' * numbers_users_length

    packet_format = FORMAT_USERS_RESPONSE.format(numbers_users_format)

    pieces = struct.unpack(packet_format, data)

    list_numbers_users = pieces[2:]

    variables = {
        keys.LIST_NUMBERS_USERS: list_numbers_users,
    }

    return variables

# parser for packet of type "USER DATA REQUEST"
def parse_user_data_request(data):

    packet_format = FORMAT_USER_DATA_REQUEST

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]
    number_user = pieces[2]

    variables = {
        keys.NUMBER_USER: number_user,
        keys.NUMBER_SESSION: number_session,
    }

    return variables

# parser for packet of type "USER DATA RESPONSE"
def parse_user_data_response(data):

    header_format = FORMAT_USER_DATA_RESPONSE.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_user = pieces[1]
    name_user_length = pieces[2]
    name_user_format = FORMAT_BLOB.format(name_user_length)

    packet_format = FORMAT_USER_DATA_RESPONSE.format(name_user_format)

    pieces = struct.unpack(packet_format, data)

    name_user_blob = pieces[3]
    name_user = str(name_user_blob, encoding='UTF-8')

    user_data = {
        keys.NUMBER_USER: number_user,
        keys.NAME_USER: name_user,
    }

    return user_data

# parser for packet of type "MESSAGE REQUEST"
def parse_message_request(data):

    header_format = FORMAT_MESSAGE_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_session = pieces[1]
    number_user = pieces[2]
    number_message = pieces[3]

    message_length = pieces[4]
    message_format = FORMAT_BLOB.format(message_length)

    packet_format = FORMAT_MESSAGE_REQUEST.format(message_format)

    pieces = struct.unpack(packet_format, data)

    message_blob = pieces[5]
    message = str(message_blob, encoding='UTF-8')

    variables = {
        keys.NUMBER_SESSION: number_session,
        keys.NUMBER_USER: number_user,
        keys.NUMBER_MESSAGE: number_message,
        keys.MESSAGE: message,
    }

    return variables

# parser for packet of type "MESSAGE RESPONSE"
def parse_message_response(data):

    packet_format = FORMAT_MESSAGE_RESPONSE

    pieces = struct.unpack(packet_format, data)

    number_message = pieces[1]

    variables = {
        keys.NUMBER_MESSAGE: number_message,
    }

    return variables

# parser for packet of type "BROADCAST REQUEST"
def parse_broadcast_request(data):

    header_format = FORMAT_BROADCAST_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_session = pieces[1]
    number_message = pieces[2]

    message_length = pieces[3]
    message_format = FORMAT_BLOB.format(message_length)

    packet_format = FORMAT_BROADCAST_REQUEST.format(message_format)

    pieces = struct.unpack(packet_format, data)

    message_blob = pieces[4]
    message = str(message_blob, encoding='UTF-8')

    variables = {
        keys.NUMBER_SESSION: number_session,
        keys.NUMBER_MESSAGE: number_message,
        keys.MESSAGE: message,
    }

    return variables

# parser for packet of type "BROADCAST RESPONSE"
def parse_broadcast_response(data):

    packet_format = FORMAT_BROADCAST_RESPONSE

    pieces = struct.unpack(packet_format, data)

    number_message = pieces[1]

    variables = {
        keys.NUMBER_MESSAGE: number_message,
    }

    return variables

# parser for packet of type "INCOMING MESSAGE REQUEST"
def parse_incoming_message_request(data):

    header_format = FORMAT_INCOMING_MESSAGE_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_user = pieces[1]
    number_message = pieces[2]

    length_message_blob = pieces[3]
    format_message_blob = FORMAT_BLOB.format(length_message_blob)

    packet_format = FORMAT_INCOMING_MESSAGE_REQUEST.format(format_message_blob)

    pieces = struct.unpack(packet_format, data)

    message_blob = pieces[4]

    message = str(message_blob, encoding='UTF-8')

    variables = {
        keys.MESSAGE: message,
        keys.NUMBER_MESSAGE: number_message,
        keys.NUMBER_USER: number_user,
    }

    return variables

# parser for packet of type "INCOMING MESSAGE RESPONSE"
def parse_incoming_message_response(data):

    packet_format = FORMAT_INCOMING_MESSAGE_RESPONSE

    pieces = struct.unpack(packet_format, data)

    number_message = pieces[1]

    variables = {
        keys.NUMBER_MESSAGE: number_message,
    }

    return variables

# parser for packet of type "FILES REQUEST"
def parse_files_request(data):

    packet_format = FORMAT_FILES_REQUEST

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]

    session_data = {
        keys.NUMBER_SESSION: number_session,
    }

    return session_data

# parser for packet of type "FILES RESPONSE"
def parse_files_response(data):

    header_format = FORMAT_FILES_RESPONSE.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    numbers_files_length = pieces[1]
    numbers_files_format = 'Q' * numbers_files_length

    packet_format = FORMAT_FILES_RESPONSE.format(numbers_files_format)

    pieces = struct.unpack(packet_format, data)

    list_numbers_files = pieces[2:]

    variables = {
        keys.LIST_NUMBERS_FILES: list_numbers_files,
    }

    return variables

# parser for packet of type "FILE DATA REQUEST"
def parse_file_data_request(data):

    packet_format = FORMAT_FILE_DATA_REQUEST

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]
    number_file_server = pieces[2]

    variables = {
        keys.NUMBER_SESSION: number_session,
        keys.NUMBER_FILE_SERVER: number_file_server,
    }

    return variables

# parser for packet of type "FILE DATA RESPONSE"
def parse_file_data_response(data):

    header_format = FORMAT_FILE_DATA_RESPONSE.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_file_server = pieces[1]
    size_file = pieces[2]
    name_file_length = pieces[3]
    name_file_format = FORMAT_BLOB.format(name_file_length)

    packet_format = FORMAT_FILE_DATA_RESPONSE.format(name_file_format)

    pieces = struct.unpack(packet_format, data)

    name_file_blob = pieces[4]
    name_file = str(name_file_blob, encoding='UTF-8')

    file_data = {
        keys.NUMBER_FILE_SERVER: number_file_server,
        keys.NAME_FILE: name_file,
        keys.SIZE_FILE: size_file,
    }

    return file_data

# parser for packet of type "FILE DOWNLOAD REQUEST"
def parse_file_download_request(data):

    packet_format = FORMAT_FILE_DOWNLOAD_REQUEST

    pieces = struct.unpack(packet_format, data)

    number_session = pieces[1]
    number_file_server = pieces[2]

    variables = {
        keys.NUMBER_SESSION: number_session,
        keys.NUMBER_FILE_SERVER: number_file_server,
    }

    return variables

# parser for packet of type "FILE DOWNLOAD RESPONSE"
def parse_file_download_response(data):

    packet_format = FORMAT_FILE_DOWNLOAD_RESPONSE

    pieces = struct.unpack(packet_format, data)

    number_file_server = pieces[1]
    transaction_download = pieces[2]

    variables = {
        keys.NUMBER_FILE_SERVER: number_file_server,
        keys.TRANSACTION_DOWNLOAD: transaction_download,
    }

    return variables

# parser for packet of type "DOWNLOAD CHUNK REQUEST"
def parse_download_chunk_request(data):

    packet_format = FORMAT_DOWNLOAD_CHUNK_REQUEST

    pieces = struct.unpack(packet_format, data)

    transaction_download = pieces[1]
    number_chunk = pieces[2]

    variables = {
        keys.TRANSACTION_DOWNLOAD: transaction_download,
        keys.NUMBER_CHUNK: number_chunk,
    }

    return variables

# parser for packet of type "DOWNLOAD CHUNK RESPONSE"
def parse_download_chunk_response(data):

    header_format = FORMAT_DOWNLOAD_CHUNK_RESPONSE.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    transaction_download = pieces[1]
    number_chunk = pieces[2]

    blob_chunk_length = pieces[3]
    blob_chunk_format = FORMAT_BLOB.format(blob_chunk_length)

    packet_format = FORMAT_DOWNLOAD_CHUNK_RESPONSE.format(blob_chunk_format)

    pieces = struct.unpack(packet_format, data)

    blob_chunk = pieces[4]

    variables = {
        keys.TRANSACTION_DOWNLOAD: transaction_download,
        keys.NUMBER_CHUNK: number_chunk,
        keys.BLOB_CHUNK: blob_chunk,
    }

    return variables

# parser for packet of type "FILE UPLOAD REQUEST"
def parse_file_upload_request(data):

    header_format = FORMAT_FILE_UPLOAD_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    number_session = pieces[1]
    size_file = pieces[2]

    length_name_file_blob = pieces[3]
    format_name_file_blob = FORMAT_BLOB.format(length_name_file_blob)

    packet_format = FORMAT_FILE_UPLOAD_REQUEST.format(format_name_file_blob)

    pieces = struct.unpack(packet_format, data)

    name_file_blob = pieces[4]
    name_file = str(name_file_blob, encoding='UTF-8')

    variables = {
        keys.NUMBER_SESSION: number_session,
        keys.SIZE_FILE: size_file,
        keys.NAME_FILE: name_file,
    }

    return variables

# parser for packet of type "FILE UPLOAD RESPONSE"
def parse_file_upload_response(data):

    packet_format = FORMAT_FILE_UPLOAD_RESPONSE

    pieces = struct.unpack(packet_format, data)

    number_file_server = pieces[1]
    transaction_upload = pieces[2]

    variables = {
        keys.NUMBER_FILE_SERVER: number_file_server,
        keys.TRANSACTION_UPLOAD: transaction_upload,
    }

    return variables

# parser for packet of type "UPLOAD CHUNK REQUEST"
def parse_upload_chunk_request(data):

    header_format = FORMAT_UPLOAD_CHUNK_REQUEST.format(constants.EMPTY_STRING)
    header_length = struct.calcsize(header_format)

    header_blob = data[0:header_length]

    pieces = struct.unpack(header_format, header_blob)

    transaction_upload = pieces[1]
    number_chunk = pieces[2]

    length_blob_chunk = pieces[3]
    format_blob_chunk = FORMAT_BLOB.format(length_blob_chunk)

    packet_format = FORMAT_UPLOAD_CHUNK_REQUEST.format(format_blob_chunk)

    pieces = struct.unpack(packet_format, data)

    blob_chunk = pieces[4]

    variables = {
        keys.TRANSACTION_UPLOAD: transaction_upload,
        keys.NUMBER_CHUNK: number_chunk,
        keys.BLOB_CHUNK: blob_chunk,
    }

    return variables

# parser for packet of type "UPLOAD CHUNK RESPONSE"
def parse_upload_chunk_response(data):

    packet_format = FORMAT_UPLOAD_CHUNK_RESPONSE

    pieces = struct.unpack(packet_format, data)

    transaction_upload = pieces[1]
    number_chunk = pieces[2]

    variables = {
        keys.TRANSACTION_UPLOAD: transaction_upload,
        keys.NUMBER_CHUNK: number_chunk,
    }

    return variables

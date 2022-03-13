import asyncio
import os
import random
import socket
import time

from . import constants, keys, packet

DEFAULT_ADDRESS = ('0.0.0.0', 55000)
DEFAULT_DELAY = 0.5 # seconds
DEFAULT_LIMIT_USERS = 64

MASK_UINT64 = 0xFFFFFFFFFFFFFFFF

SESSION_EXPIRY_TIME = 12 # seconds
TIME_NOW = time.time

# method for copying data from bytes immutable buffer to a bytearray buffer
def copy_blob_into_buffer(blob, buffer, offset=0):

    for byte in blob:
        buffer[offset] = byte
        offset = offset + 1

# class for server datagram socket
class ServerProtocol:

    # constructor
    def __init__(self, server):

        self.server = server
        self.transport = None

    # method that is called when the connection is made
    def connection_made(self, transport):
        self.transport = transport

    # method that is called when the connection is lost
    def connection_lost(self, exception):
        # TODO: log this error
        pass

    # method that is called when an error happens
    def error_received(self, exception):
        # TODO: log this error
        pass

    # method that is called when an UDP packet is received
    def datagram_received(self, data, sender):

        try:

            packet_type = packet.get_type(data)

            handler_packet = self.server.packet_handlers.get(packet_type, None)

            if handler_packet is not None:
                handler_packet(data, sender)
        
        except Exception as exception:
            # TODO: log this exception
            pass

# class for server (manager of connections, master of databases)
class Server:

    # constructor
    def __init__(self):

        self.numbers_users = {}

        self.messages = {}
        self.sessions = {}
        self.users = {}
        self.unique_numbers = set()

        self.upload_files = {}
        self.download_files = {}

        self.files = {}

        self.socket_datagram = None

        self.packet_handlers = {
            packet.TYPE_SESSION_REQUEST: self.handler_session_request,
            packet.TYPE_USERS_REQUEST: self.handler_users_request,
            packet.TYPE_USER_DATA_REQUEST: self.handler_user_data_request,
            packet.TYPE_MESSAGE_REQUEST: self.handler_message_request,
            packet.TYPE_BROADCAST_REQUEST: self.handler_broadcast_request,
            packet.TYPE_INCOMING_MESSAGE_RESPONSE: self.handler_incoming_message_response,
            packet.TYPE_FILES_REQUEST: self.handler_files_request,
            packet.TYPE_FILE_DATA_REQUEST: self.handler_file_data_request,
            packet.TYPE_FILE_DOWNLOAD_REQUEST: self.handler_file_download_request,
            packet.TYPE_DOWNLOAD_CHUNK_REQUEST: self.handler_download_chunk_request,
            packet.TYPE_FILE_UPLOAD_REQUEST: self.handler_file_upload_request,
            packet.TYPE_UPLOAD_CHUNK_REQUEST: self.handler_upload_chunk_request,
        }

    ############################################################
    # (PRIVATE) HANDLERS FOR PACKETS                           #
    ############################################################

    # method that is called when a "SESSION REQUEST" packet is received
    def handler_session_request(self, data, sender):

        variables = packet.parse_session_request(data)

        name_user = variables[keys.NAME_USER]

        # registers the user that is logging-in
        variables[keys.ADDRESS_USER] = sender
        self.helper_register_user(**variables)

        number_user = self.numbers_users[name_user]
        user_data = self.users[number_user]

        # updates remote address of user, if changed
        user_data[keys.ADDRESS_USER] = sender

        new_packet = packet.generate_session_cookie(**user_data)

        self.socket_datagram.sendto(new_packet, addr=sender)

    # method that is called when a "USERS REQUEST" packet is received
    def handler_users_request(self, data, sender):

        variables = packet.parse_users_request(data)

        number_session = variables[keys.NUMBER_SESSION]

        # only users that are logged in can request the list of users
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        list_numbers_users = [number_user for number_user in self.users]

        arguments = {
            keys.LIST_NUMBERS_USERS: list_numbers_users,
        }

        new_packet = packet.generate_users_response(**arguments)

        self.socket_datagram.sendto(new_packet, addr=sender)

    # method that is called when a "USER DATA REQUEST" packet is received
    def handler_user_data_request(self, data, sender):

        variables = packet.parse_user_data_request(data)

        number_session = variables[keys.NUMBER_SESSION]
        number_user = variables[keys.NUMBER_USER]

        # only users that are logged in can request the data from an user
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        # nothing to do if the user has not been found
        if number_user not in self.users:
            return

        user_data = self.users[number_user]

        name_user = user_data[keys.NAME_USER]

        arguments = {
            keys.NUMBER_USER: number_user,
            keys.NAME_USER: name_user,
        }

        new_packet = packet.generate_user_data_response(**arguments)

        self.socket_datagram.sendto(new_packet, addr=sender)

    # method that is called when a "MESSAGE REQUEST" packet is received
    def handler_message_request(self, data, sender):

        variables = packet.parse_message_request(data)

        number_session = variables[keys.NUMBER_SESSION]
        number_user_target = variables[keys.NUMBER_USER]
        number_message_client = variables[keys.NUMBER_MESSAGE]
        message = variables[keys.MESSAGE]

        # only users that are logged in can request the data from an user
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        # cannot send a message to a user that is not logged in
        if number_user_target not in self.users:
            return

        user_target = self.users[number_user_target]
        address_user_target = user_target[keys.ADDRESS_USER]

        data_session = self.sessions[number_session]
        number_user_source = data_session[keys.NUMBER_USER]
        number_message_server = self.helper_unique_number()

        self.messages[number_message_server] = {
            keys.NUMBER_MESSAGE: number_message_client,
            keys.NUMBER_SESSION: number_session,
            keys.ADDRESS_USER: sender,
        }

        arguments = {
            keys.NUMBER_USER: number_user_source,
            keys.NUMBER_MESSAGE: number_message_server,
            keys.MESSAGE: message,
        }

        new_packet = packet.generate_incoming_message_request(**arguments)

        self.socket_datagram.sendto(new_packet, addr=address_user_target)

    # method that is called when a "BROADCAST REQUEST" packet is received
    def handler_broadcast_request(self, data, sender):

        variables = packet.parse_broadcast_request(data)

        number_session = variables[keys.NUMBER_SESSION]
        number_message_client = variables[keys.NUMBER_MESSAGE]
        message = variables[keys.MESSAGE]

        # only users that are logged in can request the data from an user
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        data_session = self.sessions[number_session]
        number_user_source = data_session[keys.NUMBER_USER]
        number_message_server = self.helper_unique_number()

        arguments = {
            keys.NUMBER_USER: number_user_source,
            keys.NUMBER_MESSAGE: number_message_server,
            keys.MESSAGE: message,
        }

        new_packet = packet.generate_incoming_message_request(**arguments)

        for user_data in self.users.values():

            number_user_target = user_data[keys.NUMBER_USER]
            address_user_target = user_data[keys.ADDRESS_USER]

            # do not send a message to the user itself
            if number_user_target == number_user_source:
                continue

            self.socket_datagram.sendto(new_packet, addr=address_user_target)

        arguments = {
            keys.NUMBER_MESSAGE: number_message_client,
        }

        new_packet = packet_generate_broadcast_response(**arguments)
        self.socket_datagram.sendto(new_packet, addr=address_user_target)

    # method that is called when a "INCOMING MESSAGE REQUEST" packet is received
    def handler_incoming_message_response(self, data, sender):

        variables = packet.parse_incoming_message_response(data)

        number_message_server = variables[keys.NUMBER_MESSAGE]

        # nothing to do if the number message is invalid
        if number_message_server not in self.messages:
            return

        message = self.messages[number_message_server]

        number_message_client = message[keys.NUMBER_MESSAGE]
        address_user_client = message[keys.ADDRESS_USER]

        arguments = {
            keys.NUMBER_MESSAGE: number_message_client,
        }

        packet_message_response = packet.generate_message_response(**arguments)

        self.socket_datagram.sendto(
            packet_message_response,
            addr=address_user_client,
        )

        del self.messages[number_message_server]

    # method that is called when a "FILES REQUEST" packet is received
    def handler_files_request(self, data, sender):

        variables = packet.parse_files_request(data)

        number_session = variables[keys.NUMBER_SESSION]

        # only users that are logged in can request the data from a file
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        list_numbers_files = [k for k in self.files.keys()]

        arguments = {
            keys.LIST_NUMBERS_FILES: list_numbers_files,
        }

        packet_files_response = packet.generate_files_response(**arguments)

        self.socket_datagram.sendto(
            packet_files_response,
            addr=sender,
        )

    # method that is called when a "FILE DATA REQUEST" packet is received
    def handler_file_data_request(self, data, sender):

        variables = packet.parse_file_data_request(data)

        number_file_server = variables[keys.NUMBER_FILE_SERVER]
        number_session = variables[keys.NUMBER_SESSION]

        # only users that are logged in can request the data for a file
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        server_file = self.files.get(number_file_server, None)

        if server_file is None:
            return

        name_file = server_file[keys.NAME_FILE]
        size_file = server_file[keys.SIZE_FILE]

        arguments = {
            keys.NUMBER_FILE_SERVER: number_file_server,
            keys.NAME_FILE: name_file,
            keys.SIZE_FILE: size_file,
        }

        packet_file_data_response = packet.generate_file_data_response(**arguments)

        self.socket_datagram.sendto(
            packet_file_data_response,
            addr=sender,
        )

    # method that is called when a "FILE DOWNLOAD REQUEST" packet is received
    def handler_file_download_request(self, data, sender):

        variables = packet.parse_file_download_request(data)

        number_session = variables[keys.NUMBER_SESSION]
        number_file_server = variables[keys.NUMBER_FILE_SERVER]

        # only users that are logged in can download files
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        server_file = self.files.get(number_file_server, None)

        if server_file is None:
            return

        blob_file = server_file[keys.BLOB_FILE]
        transaction_download = self.helper_unique_number()

        self.download_files[transaction_download] = blob_file

        arguments = {
            keys.NUMBER_FILE_SERVER: number_file_server,
            keys.TRANSACTION_DOWNLOAD: transaction_download,
        }

        packet_file_download_response = packet.generate_file_download_response(**arguments)

        self.socket_datagram.sendto(
            packet_file_download_response,
            addr=sender,
        )

    # method that is called when a "DOWNLOAD CHUNK REQUEST" packet is received
    def handler_download_chunk_request(self, data, sender):

        variables = packet.parse_download_chunk_request(data)

        transaction_download = variables[keys.TRANSACTION_DOWNLOAD]
        number_chunk = variables[keys.NUMBER_CHUNK]

        blob_file = self.download_files.get(transaction_download, None)

        if blob_file is None:
            return

        offset_a = number_chunk * constants.SIZE_CHUNK
        offset_b = offset_a + constants.SIZE_CHUNK

        blob_chunk = blob_file[offset_a:offset_b]

        arguments = {
            keys.TRANSACTION_DOWNLOAD: transaction_download,
            keys.NUMBER_CHUNK: number_chunk,
            keys.BLOB_CHUNK: blob_chunk,
        }

        packet_download_chunk_response = packet.generate_download_chunk_response(**arguments)

        self.socket_datagram.sendto(
            packet_download_chunk_response,
            addr=sender,
        )

    # method that is called when a "FILE UPLOAD REQUEST" packet is received
    def handler_file_upload_request(self, data, sender):

        variables = packet.parse_file_upload_request(data)

        number_session = variables[keys.NUMBER_SESSION]
        size_file = variables[keys.SIZE_FILE]
        name_file = variables[keys.NAME_FILE]

        # only users that are logged in can upload files
        if number_session not in self.sessions:
            return

        # rejuvenates the session to keep it alive
        self.helper_rejuvenate_session(**variables)

        blob_file = bytearray(size_file)
        variables[keys.BLOB_FILE] = blob_file

        file_record = self.helper_file_register(**variables)
        number_file_server = file_record[keys.NUMBER_FILE_SERVER]

        transaction_upload = self.helper_unique_number()

        self.upload_files[transaction_upload] = blob_file

        arguments = {
            keys.NUMBER_FILE_SERVER: number_file_server,
            keys.TRANSACTION_UPLOAD: transaction_upload,
        }

        packet_file_upload_response = packet.generate_file_upload_response(**arguments)

        self.socket_datagram.sendto(
            packet_file_upload_response,
            addr=sender,
        )

    # method that is called when a "UPLOAD CHUNK REQUEST" packet is received
    def handler_upload_chunk_request(self, data, sender):

        variables = packet.parse_upload_chunk_request(data)

        transaction_upload = variables[keys.TRANSACTION_UPLOAD]
        number_chunk = variables[keys.NUMBER_CHUNK]
        blob_chunk = variables[keys.BLOB_CHUNK]

        buffer_file = self.upload_files.get(transaction_upload, None)

        if buffer_file is None:
            return

        offset = number_chunk * constants.SIZE_CHUNK

        copy_blob_into_buffer(blob_chunk, buffer_file, offset)

        arguments = {
            keys.TRANSACTION_UPLOAD: transaction_upload,
            keys.NUMBER_CHUNK: number_chunk,
        }

        packet_upload_chunk_response = packet.generate_upload_chunk_response(**arguments)

        self.socket_datagram.sendto(
            packet_upload_chunk_response,
            addr=sender,
        )

    ############################################################
    # (PRIVATE) HELPER METHODS                                 #
    ############################################################

    # helper method for garbage collection (disconnected users)
    def helper_janitor(self, **arguments):

        time_now = TIME_NOW()
        deleted_number_users = []
        deleted_number_sessions = []

        for number_session, session_data in self.sessions.items():

            time_session = session_data[keys.TIME_SESSION]
            number_user = session_data[keys.NUMBER_USER]

            # the time for this session has elapsed, schedule it for removal
            if time_now > time_session:
                deleted_number_users.append(number_user)
                deleted_number_sessions.append(number_session)

        # remove disconnected users
        for number_user in deleted_number_users:
            if number_user in self.users:
                del self.users[number_user]

        # remove dropped sessions
        for number_session in deleted_number_sessions:
            if number_session in self.sessions:
                del self.sessions[number_session]

    # helper method for keeping sessions alive
    def helper_rejuvenate_session(self, **arguments):

        number_session = arguments[keys.NUMBER_SESSION]

        session_data = self.sessions.get(number_session, None)

        # sesssion not found, nothing to do
        if session_data is None:
            return

        time_session = self.helper_session_expiry()
        session_data[keys.TIME_SESSION] = time_session

    # helper method for registering a user for log-in
    def helper_register_user(self, **arguments):

        address_user = arguments[keys.ADDRESS_USER]
        name_user = arguments[keys.NAME_USER]

        number_user = self.helper_unique_number()
        number_session = self.helper_unique_number()
        time_session = self.helper_session_expiry()

        self.numbers_users[name_user] = number_user

        user_data = {
            keys.ADDRESS_USER: address_user,
            keys.NUMBER_USER: number_user,
            keys.NUMBER_SESSION: number_session,
            keys.NAME_USER: name_user,
        }

        session_data = {
            keys.NUMBER_USER: number_user,
            keys.NAME_USER: name_user,
            keys.TIME_SESSION: time_session,
        }

        self.users[number_user] = user_data
        self.sessions[number_session] = session_data

    # method for calculating the expiry time of a session
    def helper_session_expiry(self, **arguments):

        session_expiry = TIME_NOW() + SESSION_EXPIRY_TIME
        return session_expiry

    # method for creating unique numbers (packet numbers, sessions)
    def helper_unique_number(self, **arguments):

        number = 0

        while True:
            number = random.randint(0, MASK_UINT64)

            if number not in self.unique_numbers:
                self.unique_numbers.add(number)
                break

        return number

    # method for registering a file into the server files list
    def helper_file_register(self, **arguments):

        name_file = arguments[keys.NAME_FILE]
        blob_file = arguments[keys.BLOB_FILE]
        size_file = arguments[keys.SIZE_FILE]
        number_file_server = self.helper_unique_number()

        file_record = {
            keys.NAME_FILE: name_file,
            keys.BLOB_FILE: blob_file,
            keys.SIZE_FILE: size_file,
            keys.NUMBER_FILE_SERVER: number_file_server,
        }

        self.files[number_file_server] = file_record

        return file_record

    ############################################################
    # PUBLIC METHODS                                           #
    ############################################################

    # method for starting the server
    async def start(self, address=DEFAULT_ADDRESS):

        socket_options = {
            'local_addr': address,
        }

        loop = asyncio.get_running_loop()
        (socket_datagram, protocol) = await loop.create_datagram_endpoint(
            lambda: ServerProtocol(self),
            **socket_options,
        )

        self.socket_datagram = socket_datagram

    # method for manually closing the server sockets
    def close(self):

        if self.socket_datagram is not None:
            self.socket_datagram.close()


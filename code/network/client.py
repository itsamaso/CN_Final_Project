import asyncio
import os
import random
import socket

from copy import copy, deepcopy

from . import constants, keys, packet

# 0.125s -> 0.25s -> 0.5s -> 1s -> 2s
DEFAULT_BASE_TIMEOUT = 0.125
DEFAULT_LIMIT_ATTEMPTS = 5

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 0
DEFAULT_ADDRESS = (DEFAULT_HOST, DEFAULT_PORT)

MASK_UINT64 = 0xFFFFFFFFFFFFFFFF

# method for copying data from bytes immutable buffer to a bytearray buffer
def copy_blob_into_buffer(blob, buffer, offset=0):

    for byte in blob:
        buffer[offset] = byte
        offset = offset + 1

# class for the asyncio UDP socket
class ClientProtocol:

    # constructor
    def __init__(self, client):
        self.transport = None
        self.client = client

    # method that is called when the socket is created
    def connection_made(self, transport):
        self.transport = transport

    # method that is called when a UDP packet is received
    def datagram_received(self, data, sender):

        try:
        
            packet_type = packet.get_type(data)

            handler_packet = self.client.packet_handlers.get(packet_type, None)

            if handler_packet is not None:
                handler_packet(data, sender)

        except Exception as exception:
            # TODO: log this exception
            pass

    # method that is called when an error occurs
    def error_received(self, exception):
        pass

    # method that is called when the connection is lost
    def connection_lost(self, exception):
        pass

    # method for manually closing the socket
    def close(self):

        if self.transport is not None:
            self.transport.close()

# class for client (user that connects to the server)
class Client:

    #  constructor
    def __init__(self):

        self.connected = False
        self.data_session = None
        self.socket_datagram = None
        self.remote_address = None

        self.unique_numbers = set()

        # map of number_user -> name_user
        self.users_data = dict()

        # map of number_user -> [message]
        self.chat_histories = dict()

        # sets of number_user
        self.client_numbers_users = set()
        self.server_numbers_users = set()

        # map of number_file -> file_data
        self.files_data = dict()

        # sets of number_file
        self.client_numbers_files = set()
        self.server_numbers_files = set()

        # list of received messages
        self.received_messages = []

        # numbers for transactions
        self.transaction_download = 0
        self.transaction_upload = 0

        self.number_chunk = 0
        self.upload_flag = False

        # object with all handlers for each packet
        self.packet_handlers = {
            packet.TYPE_SESSION_COOKIE: self.handler_session_cookie,
            packet.TYPE_USERS_RESPONSE: self.handler_users_response,
            packet.TYPE_USER_DATA_RESPONSE: self.handler_user_data_response,
            packet.TYPE_MESSAGE_RESPONSE: self.handler_message_response,
            packet.TYPE_BROADCAST_RESPONSE: self.handler_broadcast_response,
            packet.TYPE_INCOMING_MESSAGE_REQUEST: self.handler_incoming_message_request,
            packet.TYPE_FILES_RESPONSE: self.handler_files_response,
            packet.TYPE_FILE_DATA_RESPONSE: self.handler_file_data_response,
            packet.TYPE_FILE_DOWNLOAD_RESPONSE: self.handler_file_download_response,
            packet.TYPE_DOWNLOAD_CHUNK_RESPONSE: self.handler_download_chunk_response,
            packet.TYPE_FILE_UPLOAD_RESPONSE: self.handler_file_upload_response,
            packet.TYPE_UPLOAD_CHUNK_RESPONSE: self.handler_upload_chunk_response,
        }

    ############################################################
    # (PRIVATE) HANDLERS FOR PACKETS                           #
    ############################################################

    # method that is called when a "SESSION COOKIE" packet is received
    def handler_session_cookie(self, data, sender):

        self.data_session = packet.parse_session_cookie(data)
        self.remote_address = sender
        self.connected = True

    # method that is called when a "USERS RESPONSE" packet is received
    def handler_users_response(self, data, sender):

        variables = packet.parse_users_response(data)

        list_numbers_users = variables[keys.LIST_NUMBERS_USERS]

        for number_user in list_numbers_users:
            self.server_numbers_users.add(number_user)

    # method that is called when a "USER DATA RESPONSE" packet is received
    def handler_user_data_response(self, data, sender):

        variables = packet.parse_user_data_response(data)

        number_user = variables[keys.NUMBER_USER]
        name_user = variables[keys.NAME_USER]

        user_data = {
            keys.NUMBER_USER: number_user,
            keys.NAME_USER: name_user,
        }

        self.users_data[number_user] = user_data

        self.client_numbers_users.add(number_user)

    # method that is called when a "MESSAGE RESPONSE" packet is received
    def handler_message_response(self, data, sender):

        variables = packet.parse_message_response(data)

        number_message = variables[keys.NUMBER_MESSAGE]

        self.number_message = number_message

    # method that is called when a "BROADCAST RESPONSE" packet is received
    def handler_broadcast_response(self, data, sender):

        variables = packet.parse_broadcast_response(data)

        number_message = variables[keys.NUMBER_MESSAGE]

        self.number_message = number_message

    # method that is called when an "INCOMING MESSAGE REQUEST" packet is received
    def handler_incoming_message_request(self, data, sender):

        variables = packet.parse_incoming_message_request(data)

        number_user_source = variables[keys.NUMBER_USER]
        number_message = variables[keys.NUMBER_MESSAGE]
        message = variables[keys.MESSAGE]

        chat_history = self.chat_histories.get(number_user_source, [])
        chat_history.append(message)

        self.chat_histories[number_user_source] = chat_history

        arguments = {
            keys.NUMBER_MESSAGE: number_message,
        }

        new_packet = packet.generate_incoming_message_response(**arguments)

        self.socket_datagram.sendto(new_packet, addr=self.remote_address)

    # method that is called when a "FILES RESPONSE" packet is received
    def handler_files_response(self, data, sender):

        variables = packet.parse_files_response(data)

        list_numbers_files = variables[keys.LIST_NUMBERS_FILES]

        for number_file in list_numbers_files:
            self.server_numbers_files.add(number_file)

    # method that is called when a "FILE DATA RESPONSE" packet is received
    def handler_file_data_response(self, data, sender):

        variables = packet.parse_file_data_response(data)

        number_file_server = variables[keys.NUMBER_FILE_SERVER]
        name_file = variables[keys.NAME_FILE]
        size_file = variables[keys.SIZE_FILE]

        file_data = {
            keys.NUMBER_FILE_SERVER: number_file_server,
            keys.NAME_FILE: name_file,
            keys.SIZE_FILE: size_file,
        }

        self.files_data[number_file_server] = file_data

        self.client_numbers_files.add(number_file_server)

    # method that is called when a "FILE DOWNLOAD RESPONSE" packet is received
    def handler_file_download_response(self, data, sender):

        variables = packet.parse_file_download_response(data)

        self.transaction_download = variables[keys.TRANSACTION_DOWNLOAD]

    def handler_download_chunk_response(self, data, sender):

        variables = packet.parse_download_chunk_response(data)

        number_chunk = variables[keys.NUMBER_CHUNK]

        if number_chunk == self.number_chunk:

            self.number_chunk = self.number_chunk + 1
            self.chunk_data = variables

    # method that is called when a "FILE UPLOAD RESPONSE" packet is received
    def handler_file_upload_response(self, data, sender):

        variables = packet.parse_file_upload_response(data)

        self.transaction_upload = variables[keys.TRANSACTION_UPLOAD]

    # method that is called when a "UPLOAD CHUNK RESPONSE" packet is received
    def handler_upload_chunk_response(self, data, sender):

        variables = packet.parse_upload_chunk_response(data)

        number_chunk = variables[keys.NUMBER_CHUNK]

        if number_chunk == self.number_chunk:

            self.number_chunk = self.number_chunk + 1
            self.upload_flag = True

    ############################################################
    # (PRIVATE) SENDERS OF PACKETS                             #
    ############################################################

    # method for sending a "SESSION REQUEST" packet
    def sender_session_request(self, **arguments):

        host = arguments.get(keys.HOST, DEFAULT_HOST)
        port = arguments.get(keys.PORT, DEFAULT_PORT)

        remote_address = (host, port)

        packet_session_request = packet.generate_session_request(**arguments)

        self.socket_datagram.sendto(
            packet_session_request,
            addr=remote_address,
        )

    # method for sending a "USERS REQUEST" packet
    def sender_users_request(self, **arguments):

        packet_users_request = packet.generate_users_request(**arguments)

        self.socket_datagram.sendto(
            packet_users_request,
            addr=self.remote_address,
        )

    # method for sending a "USER DATA REQUEST" packet
    def sender_user_data_request(self, **arguments):

        packet_user_data_request = packet.generate_user_data_request(**arguments)

        self.socket_datagram.sendto(
            packet_user_data_request,
            addr=self.remote_address,
        )

    # method for sending a "MESSAGE REQUEST" packet
    def sender_message_request(self, **arguments):

        packet_message_request = packet.generate_message_request(**arguments)

        self.socket_datagram.sendto(
            packet_message_request,
            addr=self.remote_address,
        )

    # method for sending a "BROADCAST REQUEST" packet
    def sender_broadcast_request(self, **arguments):

        packet_broadcast_request = packet.generate_broadcast_request(**arguments)

        self.socket_datagram.sendto(
            packet_broadcast_request,
            addr=self.remote_address,
        )

    # method for sending a "FILES REQUEST" packet
    def sender_files_request(self, **arguments):

        packet_files_request = packet.generate_files_request(**arguments)

        self.socket_datagram.sendto(
            packet_files_request,
            addr=self.remote_address,
        )

    # method for sending a "FILE DATA REQUEST" packet
    def sender_file_data_request(self, **arguments):

        packet_file_data_request = packet.generate_file_data_request(**arguments)

        self.socket_datagram.sendto(
            packet_file_data_request,
            addr=self.remote_address,
        )

    # method for sending a "FILE DOWNLOAD REQUEST" packet
    def sender_file_download_request(self, **arguments):

        packet_file_download_request = packet.generate_file_download_request(**arguments)

        self.socket_datagram.sendto(
            packet_file_download_request,
            addr=self.remote_address,
        )

    # method for sending a "DOWNLOAD CHUNK REQUEST" packet
    def sender_download_chunk_request(self, **arguments):

        packet_download_chunk_request = packet.generate_download_chunk_request(**arguments)

        self.socket_datagram.sendto(
            packet_download_chunk_request,
            addr=self.remote_address,
        )

    # method for sending a "FILE UPLOAD REQUEST" packet
    def sender_file_upload_request(self, **arguments):

        packet_file_upload_request = packet.generate_file_upload_request(**arguments)

        self.socket_datagram.sendto(
            packet_file_upload_request,
            addr=self.remote_address,
        )

    # method for sending a "UPLOAD CHUNK REQUEST" packet
    def sender_upload_chunk_request(self, **arguments):

        packet_upload_chunk_request = packet.generate_upload_chunk_request(**arguments)

        self.socket_datagram.sendto(
            packet_upload_chunk_request,
            addr=self.remote_address,
        )

    ############################################################
    # (PRIVATE) HELPER METHODS                                 #
    ############################################################

    # helper method for generating unique numbers, (packet numbers, sessions)
    def helper_unique_number(self, **arguments):

        number = 0

        while True:
            number = random.randint(0, MASK_UINT64)

            if number not in self.unique_numbers:
                self.unique_numbers.add(number)
                break

        return number

    ############################################################
    # PUBLIC METHODS                                           #
    ############################################################

    # method that starts the client object, creating sockets and other set-up
    async def start(self, address=DEFAULT_ADDRESS):

        socket_options = {
            'local_addr': address,
        }

        loop = asyncio.get_running_loop()
        (socket_datagram, protocol) = await loop.create_datagram_endpoint(
            lambda: ClientProtocol(self),
            **socket_options,
        )

        self.socket_datagram = socket_datagram

    # method that connects an user to the server
    async def connect(self, **arguments):

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        self.data_session = None

        attempts = 0
        while attempts < limit_attempts:

            self.sender_session_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully made a session with the server
            if self.data_session is not None:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        return copy(self.data_session)

    # method that retrieves the list of online users from the server
    async def users_request(self, **arguments):

        # nothing to do if the client is not connected
        if not self.connected:
            return None

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        sender_arguments[keys.NUMBER_SESSION] = number_session

        # clears the cache of users numbers received from server
        self.server_numbers_users.clear()

        attempts = 0
        while attempts < limit_attempts:

            self.sender_users_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully received users numbers from server
            if len(self.server_numbers_users) > 0:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # no data received from server, error
        if len(self.server_numbers_users) == 0:
            return None

        # nothing has changed, we can use the cache to return early
        if self.server_numbers_users == self.client_numbers_users:
            return deepcopy(self.users_data)

        # something has changed, invalidate client cache
        self.client_numbers_users.clear()
        self.users_data.clear()

        attempts = 0
        while attempts < limit_attempts:

            # request user data for every user number
            for number_user in self.server_numbers_users:

                # no need to request a user data that we already have
                if number_user in self.client_numbers_users:
                    continue

                sender_arguments[keys.NUMBER_USER] = number_user
                self.sender_user_data_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            length_client = len(self.client_numbers_users)
            length_server = len(self.server_numbers_users)

            # successfully received all user data from server
            if length_client == length_server:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # no user data received from server, error
        if len(self.client_numbers_users) == 0:
            return None

        return deepcopy(self.users_data)

    # method that sends a message to a specific user
    async def send_message(self, **arguments):

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        number_message = self.helper_unique_number()

        sender_arguments[keys.NUMBER_SESSION] = number_session
        sender_arguments[keys.NUMBER_MESSAGE] = number_message

        self.number_message = 0

        attempts = 0
        while attempts < limit_attempts:

            self.sender_message_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully received delivery acknowledgement from server
            if self.number_message == number_message:
                return True

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # failed to receive delivery acknowledgement from server
        return False

    # method that sends a message to all users
    async def broadcast_message(self, **arguments):

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        number_message = self.helper_unique_number()

        sender_arguments[keys.NUMBER_SESSION] = number_session
        sender_arguments[keys.NUMBER_MESSAGE] = number_message

        self.number_message = 0

        self.sender_broadcast_request(**sender_arguments)

    # method that loads the chat history for the user
    async def chat_history(self, **arguments):

        number_user = arguments[keys.NUMBER_USER]

        chat_history = self.chat_histories.get(number_user, None)

        return copy(chat_history)

    # method that request the list of files from the server
    async def files_request(self, **arguments):

        # nothing to do if the client is not connected
        if not self.connected:
            return None

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        sender_arguments[keys.NUMBER_SESSION] = number_session

        # clears the cache of files numbers received from server
        self.server_numbers_files.clear()

        attempts = 0
        while attempts < limit_attempts:

            self.sender_files_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully received files numbers from server
            if len(self.server_numbers_files) > 0:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # no data received from server, error
        if len(self.server_numbers_files) == 0:
            return None

        # nothing has changed, we can use the cache to return early
        if self.server_numbers_files == self.client_numbers_files:
            return deepcopy(self.files_data)

        # something has changed, invalidate client cache
        self.client_numbers_files.clear()
        self.files_data.clear()

        attempts = 0
        while attempts < limit_attempts:

            # request file data for every file number
            for number_file in self.server_numbers_files:

                # no need to request a user data that we already have
                if number_file in self.client_numbers_files:
                    continue

                sender_arguments[keys.NUMBER_FILE_SERVER] = number_file
                self.sender_file_data_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            length_client = len(self.client_numbers_files)
            length_server = len(self.server_numbers_files)

            # successfully received all user data from server
            if length_client == length_server:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # no file data received from server, error
        if len(self.client_numbers_files) == 0:
            return None

        return deepcopy(self.files_data)

    # method that download a file from the server
    async def download_file(self, **arguments):

        # nothing to do if the client is not connected
        if not self.connected:
            return False

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        sender_arguments[keys.NUMBER_SESSION] = number_session

        # clears the number for transaction download
        self.transaction_download = 0

        attempts = 0
        while attempts < limit_attempts:

            self.sender_file_download_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully made a download transaction with the server
            if self.transaction_download != 0:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # failed to make a download transaction
        if self.transaction_download == 0:
            return False

        sender_arguments[keys.TRANSACTION_DOWNLOAD] = self.transaction_download

        path_output = arguments[keys.PATH_OUTPUT]
        output_file = open(path_output, 'wb')

        size_file = arguments[keys.SIZE_FILE]
        count_chunks = (size_file + constants.LIMIT_CHUNK) / constants.SIZE_CHUNK

        self.number_chunk = 0

        all_received = False
        while not all_received:

            # all download chunks have been received, break loop
            if self.number_chunk >= count_chunks:
                break

            sender_arguments[keys.NUMBER_CHUNK] = self.number_chunk

            wait_time = arguments.get(
                keys.BASE_TIMEOUT,
                DEFAULT_BASE_TIMEOUT,
            )

            attempts = 0
            while attempts < limit_attempts:

                self.chunk_data = None

                # requests file chunk from server
                self.sender_download_chunk_request(**sender_arguments)

                # sleeps in order to give time to server for replying
                await asyncio.sleep(wait_time)

                # successfully received chunk from server
                if self.chunk_data is not None:

                    blob_chunk = self.chunk_data[keys.BLOB_CHUNK]
                    output_file.write(blob_chunk)
                    break

                # increases wait time on each failure
                wait_time = wait_time + wait_time

                attempts = attempts + 1

            # failed to retrieve chunk
            if attempts == limit_attempts:
                return False

        output_file.close()

        return True

    # method for uploading a file to the server
    async def upload_file(self, **arguments):

        # nothing to do if the client is not connected
        if not self.connected:
            return False

        wait_time = arguments.get(
            keys.BASE_TIMEOUT,
            DEFAULT_BASE_TIMEOUT,
        )

        limit_attempts = arguments.get(
            keys.LIMIT_ATTEMPTS,
            DEFAULT_LIMIT_ATTEMPTS,
        )

        sender_arguments = copy(arguments)

        number_session = self.data_session[keys.NUMBER_SESSION]
        sender_arguments[keys.NUMBER_SESSION] = number_session

        # clears the number for transaction upload
        self.transaction_upload = 0

        attempts = 0
        while attempts < limit_attempts:

            self.sender_file_upload_request(**sender_arguments)

            # sleeps in order to give time to server for replying
            await asyncio.sleep(wait_time)

            # successfully made a upload transaction with the server
            if self.transaction_upload != 0:
                break

            # increases wait time on each failure
            wait_time = wait_time + wait_time

            attempts = attempts + 1

        # failed to make a upload transaction
        if self.transaction_upload == 0:
            return False

        sender_arguments[keys.TRANSACTION_UPLOAD] = self.transaction_upload

        path_input = arguments[keys.PATH_INPUT]
        input_file = open(path_input, 'rb')

        size_file = os.path.getsize(path_input)
        count_chunks = (size_file + constants.LIMIT_CHUNK) / constants.SIZE_CHUNK

        self.number_chunk = 0

        all_sent = False
        while not all_sent:

            # all upload chunks have been sent, break loop
            if self.number_chunk >= count_chunks:
                break

            wait_time = arguments.get(
                keys.BASE_TIMEOUT,
                DEFAULT_BASE_TIMEOUT,
            )

            blob_chunk = input_file.read(constants.SIZE_CHUNK)

            sender_arguments[keys.BLOB_CHUNK] = blob_chunk
            sender_arguments[keys.NUMBER_CHUNK] = self.number_chunk

            attempts = 0
            while attempts < limit_attempts:

                self.upload_flag = False

                # requests file chunk to server
                self.sender_upload_chunk_request(**sender_arguments)

                # sleeps in order to give time to server for replying
                await asyncio.sleep(wait_time)

                # successfully sent chunk to server
                if self.upload_flag:
                    break

                # increases wait time on each failure
                wait_time = wait_time + wait_time

                attempts = attempts + 1

            # failed to send chunk
            if attempts == limit_attempts:
                return False

        input_file.close()

        return True

    # method for manually closing the client
    def close(self):

        if self.socket_datagram is not None:
            self.socket_datagram.close()

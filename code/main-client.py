import asyncio
import os
import tkinter

from copy import copy

from network import constants, client, keys

INTERVAL_JANITOR = 5 # seconds

MAIN_SLEEP = 0.03125 # seconds

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 55000

SITUATION_OFFLINE = 'NOT LOGGED IN!'
SITUATION_CONNECTING = 'TRYING TO LOG IN...'
SITUATION_ONLINE = 'LOGGED IN AS \'{}\''
SITUATION_FAILURE = 'FAILED TO LOG-IN!'

TITLE_APP = 'Chatting Application'
font_specs = ("Helvetica", 10, "bold")


# method for dispatching events into the asyncio loop
def event_dispatch(loop, action):

    def event_handler(event):
        coroutine = action(event)
        loop.create_task(coroutine)

    return event_handler


# main method for the client
async def main():

    loop = asyncio.get_running_loop()
    application_alive = True

    # variables shared across multiple actions
    list_online_users = []
    list_server_files = []
    partner_data = None
    server_file = None

    # sets up the client object 
    main_client = client.Client()
    await main_client.start()

    # INTERFACE_ROOT

    interface_root = tkinter.Tk()
    interface_root.resizable(width=False, height=False)
    interface_root.title(TITLE_APP)
    interface_root.configure(bg='beige')

    # LABEL: NAME_USER

    options_name_user = {
        'text': 'Name:',
    }

    grid_name_user = {
        'row': 0,
        'column': 0,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'E',
    }

    label_name_user = tkinter.Label(
        interface_root,
        **options_name_user,
    )

    label_name_user.grid(**grid_name_user)
    label_name_user.configure(bg='beige')
    label_name_user.configure(font=font_specs)

    # ENTRY: INPUT_NAME

    variable_input_name = tkinter.StringVar()

    options_input_name = {
        'textvariable': variable_input_name,
    }

    grid_input_name = {
        'row': 0,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    entry_input_name = tkinter.Entry(
        interface_root,
        **options_input_name,
    )

    entry_input_name.grid(**grid_input_name)

    # BUTTON: USER_CONNECT

    options_user_connect = {
        'text': 'Connect',
    }

    grid_user_connect = {
        'row': 0,
        'column': 2,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'W',
    }

    button_user_connect = tkinter.Button(
        interface_root,
        **options_user_connect,
    )

    button_user_connect.grid(**grid_user_connect)
    button_user_connect.configure(bg='beige')
    button_user_connect.configure(font=font_specs)

    # LABEL: SITUATION

    options_situation = {
        'text': SITUATION_OFFLINE,
    }

    grid_situation = {
        'row': 1,
        'column': 0,
        'rowspan': 1,
        'columnspan': 3,
        'sticky': 'EW',
    }

    label_situation = tkinter.Label(
        interface_root,
        **options_situation,
    )

    label_situation.grid(**grid_situation)
    label_situation.configure(bg='firebrick', fg='beige')
    label_situation.configure(font=font_specs)

    # FRAME: COMMUNICATION_BOX

    options_communication_box = {

    }

    grid_communication_box = {
        'row': 2,
        'column': 0,
        'rowspan': 1,
        'columnspan': 3,
        'sticky': 'EW',
    }

    frame_communication_box = tkinter.Frame(
        interface_root,
        **options_communication_box,
    )

    frame_communication_box.grid(**grid_communication_box)

    # LISTBOX: ONLINE_USERS

    variable_online_users = tkinter.StringVar()

    options_online_users = {
        'listvariable': variable_online_users,
    }

    grid_online_users = {
        'row': 0,
        'column': 0,
        'rowspan': 2,
        'columnspan': 1,
        'sticky': 'SN',
    }

    listbox_online_users = tkinter.Listbox(
        frame_communication_box,
        **options_online_users,
    )

    listbox_online_users.grid(**grid_online_users)
    listbox_online_users.configure(bg='beige')
    listbox_online_users.configure(font=font_specs)

    # LISTBOX: RECEIVED_MESSAGES

    variable_received_messages = tkinter.StringVar()

    options_received_messages = {
        'listvariable': variable_received_messages,
    }

    grid_received_messages = {
        'row': 0,
        'column': 1,
        'rowspan': 1,
        'columnspan': 4,
        'sticky': 'EW',
    }

    listbox_received_messages = tkinter.Listbox(
        frame_communication_box,
        **options_received_messages,
    )

    listbox_received_messages.grid(**grid_received_messages)
    listbox_received_messages.configure(bg='white')
    listbox_received_messages.configure(font=font_specs)

    # LABEL: NEW_MESSAGE

    options_new_message = {
        'text': 'Insert A Message:'
    }

    grid_new_message = {
        'row': 1,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    label_new_message = tkinter.Label(
        frame_communication_box,
        **options_new_message,
    )

    label_new_message.grid(**grid_new_message)
    label_new_message.configure(bg='beige')
    label_new_message.configure(font=font_specs)

    # ENTRY: INPUT_MESSAGE

    variable_input_message = tkinter.StringVar()

    options_input_message = {
        'textvariable': variable_input_message,
    }

    grid_input_message = {
        'row': 1,
        'column': 2,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    entry_input_message = tkinter.Entry(
        frame_communication_box,
        **options_input_message,
    )

    entry_input_message.grid(**grid_input_message)
    entry_input_message.configure(font=font_specs)

    # BUTTON: SUBMIT_MESSAGE

    options_submit_message = {
        'text': 'Send',
    }

    grid_submit_message = {
        'row': 1,
        'column': 3,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    button_submit_message = tkinter.Button(
        frame_communication_box,
        **options_submit_message,
    )

    button_submit_message.grid(**grid_submit_message)
    button_submit_message.configure(bg='beige')
    button_submit_message.configure(font=font_specs)

    # BUTTON: BROADCAST_MESSAGE

    options_broadcast_message = {
        'text': 'Broadcast',
    }

    grid_broadcast_message = {
        'row': 1,
        'column': 4,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    button_broadcast_message = tkinter.Button(
        frame_communication_box,
        **options_broadcast_message,
    )

    button_broadcast_message.grid(**grid_broadcast_message)
    button_broadcast_message.configure(bg='beige')
    button_broadcast_message.configure(font=font_specs)

    # LABEL: FILES_SERVER

    options_files_server = {
        'text': "Files Section:",
    }

    grid_files_server = {
        'row': 3,
        'column': 0,
        'rowspan': 1,
        'columnspan': 3,
        'sticky': 'EW',
    }

    label_files_server = tkinter.Label(
        interface_root,
        **options_files_server,
    )

    label_files_server.grid(**grid_files_server)
    label_files_server.configure(bg='firebrick', fg='beige')
    label_files_server.configure(font=font_specs)

    # FRAME: FILES_BOX

    options_files_box = {

    }

    grid_files_box = {
        'row': 4,
        'column': 0,
        'rowspan': 1,
        'columnspan': 3,
        'sticky': 'EW',
    }

    frame_files_box = tkinter.Frame(
        interface_root,
        **options_files_box,
    )

    frame_files_box.grid(**grid_files_box)
    frame_files_box.configure(bg='beige')

    # LISTBOX: FILES_LIST

    variable_files_list = tkinter.StringVar()

    options_files_list = {
        'listvariable': variable_files_list,
    }

    grid_files_list = {
        'row': 0,
        'column': 0,
        'rowspan': 2,
        'columnspan': 1,
        'sticky': 'SN',
    }

    listbox_files_list = tkinter.Listbox(
        frame_files_box,
        **options_files_list,
    )

    listbox_files_list.grid(**grid_files_list)
    listbox_files_list.configure(bg='beige')

    # FRAME: UPLOAD_BOARD

    options_upload_board = {

    }

    grid_upload_board = {
        'row': 0,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'NS',
    }

    frame_upload_board = tkinter.Frame(
        frame_files_box,
        **options_upload_board,
    )

    frame_upload_board.grid(**grid_upload_board)
    frame_upload_board.configure(bg='beige')

    # LABEL: UPLOAD_PATH

    options_upload_path = {
        'text': '   Insert A Path:',
    }

    grid_upload_path = {
        'row': 1,
        'column': 0,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'E',
    }

    label_upload_path = tkinter.Label(
        frame_upload_board,
        **options_upload_path,
    )

    label_upload_path.grid(**grid_upload_path)
    label_upload_path.configure(bg='beige')
    label_upload_path.configure(font=font_specs)

    # ENTRY: INPUT_UPLOAD

    variable_input_upload = tkinter.StringVar()

    options_input_upload = {
        'textvariable': variable_input_upload,
    }

    grid_input_upload = {
        'row': 1,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    entry_input_upload = tkinter.Entry(
        frame_upload_board,
        **options_input_upload,
    )

    entry_input_upload.grid(**grid_input_upload)

    # BUTTON: SUBMIT_UPLOAD

    options_submit_upload = {
        'text': 'Upload',
    }

    grid_submit_upload = {
        'row': 1,
        'column': 2,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'W',
    }

    button_submit_upload = tkinter.Button(
        frame_upload_board,
        **options_submit_upload,
    )

    button_submit_upload.grid(**grid_submit_upload)
    button_submit_upload.configure(bg='beige')
    button_submit_upload.configure(font=font_specs)

    # FRAME: DOWNLOAD_BOARD

    options_download_board = {

    }

    grid_download_board = {
        'row': 1,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'NS',
    }

    frame_download_board = tkinter.Frame(
        frame_files_box,
        **options_download_board,
    )

    frame_download_board.grid(**grid_download_board)
    frame_download_board.configure(bg='beige')

    # LABEL: DOWNLOAD_PATH

    options_download_path = {
        'text': 'Insert A Path:',
    }

    grid_download_path = {
        'row': 0,
        'column': 0,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'E',
    }

    label_download_path = tkinter.Label(
        frame_download_board,
        **options_download_path,
    )

    label_download_path.grid(**grid_download_path)
    label_download_path.configure(bg='beige')
    label_download_path.configure(font=font_specs)

    # ENTRY: INPUT_UPLOAD

    variable_input_download = tkinter.StringVar()

    options_input_download = {
        'textvariable': variable_input_download,
    }

    grid_input_download = {
        'row': 0,
        'column': 1,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'EW',
    }

    entry_input_download = tkinter.Entry(
        frame_download_board,
        **options_input_download,
    )

    entry_input_download.grid(**grid_input_download)

    # BUTTON: SUBMIT_DOWNLOAD

    options_submit_download = {
        'text': 'Save',
    }

    grid_submit_download = {
        'row': 0,
        'column': 2,
        'rowspan': 1,
        'columnspan': 1,
        'sticky': 'W',
    }

    button_submit_download = tkinter.Button(
        frame_download_board,
        **options_submit_download,
    )

    button_submit_download.grid(**grid_submit_download)
    button_submit_download.configure(bg='beige')
    button_submit_download.configure(font=font_specs)

    # BIND EVENT: <ButtonRelease> BUTTON(USER_CONNECT)

    async def action_user_connect(event):

        nonlocal main_client
        nonlocal entry_input_name
        nonlocal label_situation

        name_user = entry_input_name.get()

        label_situation.config(text=SITUATION_CONNECTING)

        arguments_main_client = {
            keys.NAME_USER: name_user,
            keys.HOST: SERVER_HOST,
            keys.PORT: SERVER_PORT,
        }

        data_session = await main_client.connect(**arguments_main_client)

        if data_session is None:
            label_situation.config(text=SITUATION_FAILURE)
            return

        label_situation.config(text=SITUATION_ONLINE.format(name_user))

    dispatch_user_connect = event_dispatch(loop, action_user_connect)

    button_user_connect.bind('<ButtonRelease>', dispatch_user_connect)

    # BIND EVENT: <<ListboxSelect>> LISTBOX(ONLINE_USERS)

    async def action_online_users(event):

        nonlocal list_online_users
        nonlocal listbox_online_users
        nonlocal partner_data

        indexes = [index for index in listbox_online_users.curselection()]

        if len(indexes) == 0:
            return

        index = indexes[0]

        partner_data = list_online_users[index]

    dispatch_online_users = event_dispatch(loop, action_online_users)

    listbox_online_users.bind('<<ListboxSelect>>', dispatch_online_users)

    # BIND EVENT: <ButtonRelease> BUTTON(SUBMIT_MESSAGE)

    async def action_submit_message(event):

        nonlocal main_client
        nonlocal partner_data
        nonlocal variable_input_message

        # nothing to do if the client is not connected
        if not main_client.connected:
            return

        message = variable_input_message.get()
        variable_input_message.set(constants.EMPTY_STRING)

        if partner_data is not None:

            arguments = copy(partner_data)
            arguments[keys.MESSAGE] = message

            await main_client.send_message(**arguments)

    dispatch_submit_message = event_dispatch(loop, action_submit_message)

    button_submit_message.bind('<ButtonRelease>', dispatch_submit_message)

    # BIND EVENT: <ButtonRelease> BUTTON(BROADCAST_MESSAGE)

    async def action_broadcast_message(event):

        nonlocal main_client
        nonlocal variable_input_message

        # nothing to do if the client is not connected
        if not main_client.connected:
            return

        message = variable_input_message.get()
        variable_input_message.set(constants.EMPTY_STRING)
        arguments = {}
        arguments[keys.MESSAGE] = message

        await main_client.broadcast_message(**arguments)

    dispatch_broadcast_message = event_dispatch(loop, action_broadcast_message)

    button_broadcast_message.bind('<ButtonRelease>', dispatch_broadcast_message)

    # BIND EVENT: <ButtonRelease> BUTTON(SUBMIT_UPLOAD)

    async def action_submit_upload(event):

        nonlocal main_client
        nonlocal variable_input_upload

        upload_path = variable_input_upload.get()

        # nothing to do if the client is not connected
        if not main_client.connected:
            return

        print('[UPLOADING FILE]')
        arguments = {}
        arguments[keys.PATH_INPUT] = upload_path
        arguments[keys.SIZE_FILE] = os.path.getsize(upload_path)
        arguments[keys.NAME_FILE] = os.path.basename(upload_path)
        await main_client.upload_file(**arguments)
        print('[FILE UPLOADED!]')

    dispatch_submit_upload = event_dispatch(loop, action_submit_upload)

    button_submit_upload.bind('<ButtonRelease>', dispatch_submit_upload)

    # BIND EVENT: <ButtonRelease> BUTTON(SUBMIT_DOWNLOAD)

    async def action_submit_download(event):

        nonlocal main_client
        nonlocal server_file
        nonlocal variable_input_download

        download_path = variable_input_download.get()

        if server_file is not None:

            print('[DOWNLOADING FILE]')
            arguments = copy(server_file)
            arguments[keys.PATH_OUTPUT] = download_path
            await main_client.download_file(**arguments)
            print('[FILE DOWNLOADED!]')

        # nothing to do if the client is not connected
        if not main_client.connected:
            return

        if server_file is not None:
            # TODO: download file from server
            pass

        # await main_client.send_download(**arguments)

    dispatch_submit_download = event_dispatch(loop, action_submit_download)

    button_submit_download.bind('<ButtonRelease>', dispatch_submit_download)

    # BIND EVENT: <<ListboxSelect>> LISTBOX(FILES_LIST)
    async def action_files_list(event):

        nonlocal list_server_files
        nonlocal listbox_files_list
        nonlocal server_file

        indexes = [index for index in listbox_files_list.curselection()]

        if len(indexes) == 0:
            return

        index = indexes[0]

        server_file = list_server_files[index]

    dispatch_files_list = event_dispatch(loop, action_files_list)

    listbox_files_list.bind('<<ListboxSelect>>', dispatch_files_list)

    # PROTOCOL: 'WM_DELETE_WINDOW' FOR INTERFACE_ROOT

    def shutdown_application():
        nonlocal application_alive
        application_alive = False

    # calls shutdown_application when the main window is destroyed
    interface_root.protocol('WM_DELETE_WINDOW', shutdown_application)

    # INTERVAL JANITOR

    counter = 0

    # method that is called every once in a while for clean-up
    async def janitor_procedure():

        await asyncio.sleep(INTERVAL_JANITOR)

        nonlocal counter

        nonlocal partner_data
        nonlocal list_online_users
        nonlocal list_server_files
        nonlocal main_client
        nonlocal variable_online_users
        nonlocal variable_received_messages

        users_data = await main_client.users_request()

        if users_data is not None:

            list_online_users = []
            names_online_users = []

            for user_data in users_data.values():

                name_user = user_data[keys.NAME_USER]

                list_online_users.append(user_data)
                names_online_users.append(name_user)

            # updates the listbox with the list of online users
            variable_online_users.set(names_online_users)

        if partner_data is not None:
            partner_chat_history = await main_client.chat_history(**partner_data)

            if partner_chat_history is not None:
                variable_received_messages.set(partner_chat_history)

        files_data = await main_client.files_request()

        if files_data is not None:

            list_server_files = []
            names_server_files = []

            for file_data in files_data.values():

                name_file = file_data[keys.NAME_FILE]

                list_server_files.append(file_data)
                names_server_files.append(name_file)

            variable_files_list.set(names_server_files)
        
        # sets this in order to allow for the janitor to run again
        coroutine_janitor = janitor_procedure()
        loop.create_task(coroutine_janitor)

    # starts the janitor interval
    coroutine_janitor = janitor_procedure()
    loop.create_task(coroutine_janitor)

    # main loop that controls the application
    while application_alive:

        # refreshes the graphical user interface
        interface_root.update()

        # sleep in order to let other tasks to be run
        await asyncio.sleep(MAIN_SLEEP)

coroutine_main = main()
asyncio.run(coroutine_main)

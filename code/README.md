# PYTHON CHAT APP

## INTRODUCTION

## PACKET TYPES AND FORMATS

The first two octets of every packet determine what is the type of the packet.

### PACKET TYPE #1: SESSION REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0002h | SIZE FOR NAME USER (SZ1)                             |
| SZ1   | BLOB FOR NAME USER                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #2: SESSION COOKIE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR USER                                      |
| 0008h | NUMBER FOR SESSION                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #4: SESSION PRESERVE (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
+-------+------------------------------------------------------+
```

If the user does not send any packet after a given amount of time (currently, thirty seconds),
 the server assumes that the user has disconnected and closes the session. In order to prevent this, the client should, in the event that it wishes to continue with the session, send this message in order to preserve it.

 Notice that other session actions (sending messages, broadcasting messages, uploading files) also refresh the session, so this packet should only be sent from the client when it is idle.

 On success, the server replies with a 'SESSION COOKIE' message.

### PACKET TYPE #5: USERS REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #6: USERS RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0002h | LENGTH L1 OF ARRAY OF USERS NUMBERS (SZ1 = L1 * 8)   |
| SZ1   | ARRAY OF USERS NUMBERS                               |
+-------+------------------------------------------------------+
```

### PACKET TYPE #7: USER DATA REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0008h | NUMBER FOR USER                                      |
+-------+------------------------------------------------------+
```

### PACKET TYPE #8: USER DATA RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR USER                                      |
| 0002h | SIZE FOR NAME USER (SZ1)                             |
| SZ1   | BLOB FOR NAME USER                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #9: MESSAGE REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0008h | NUMBER FOR USER (DESTINATION)                        |
| 0008h | NUMBER FOR MESSAGE                                   |
| 0002h | LENGTH L1 OF MESSAGE BLOB (SZ1 = L1 * 1)             |
| SZ1   | MESSAGE BLOB                                         |
+-------+------------------------------------------------------+
```

### PACKET TYPE #10: MESSAGE RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR MESSAGE                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #11: BROADCAST REQUEST (CLIENT -> SERVER)

+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0008h | NUMBER FOR MESSAGE                                   |
| 0002h | LENGTH L1 OF MESSAGE BLOB (SZ1 = L1 * 1)             |
| SZ1   | MESSAGE BLOB                                         |
+-------+------------------------------------------------------+

### PACKET TYPE #12: BROADCAST RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR MESSAGE                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #13: INCOMING MESSAGE REQUEST (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR USER (SENDER)                             |
| 0008h | NUMBER FOR MESSAGE                                   |
| 0002h | LENGTH L1 OF MESSAGE BLOB (SZ1 = L1 * 1)             |
| SZ1   | MESSAGE BLOB                                         |
+-------+------------------------------------------------------+
```

### PACKET TYPE #14: INCOMING MESSAGE RESPONSE (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR MESSAGE                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #19: FILES REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #20: FILES RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0002h | LENGTH L1 OF ARRAY OF FILES NUMBERS (SZ1 = L1 * 8)   |
| SZ1   | ARRAY OF FILES NUMBERS                               |
+-------+------------------------------------------------------+
```

### PACKET TYPE #21: FILE DATA REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0008h | NUMBER FOR FILE (SERVER)                             |
+-------+------------------------------------------------------+
```

### PACKET TYPE #22: FILE DATA RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR FILE (SERVER)                             |
| 0004h | SIZE OF FILE                                         |
| 0002h | SIZE FOR NAME FILE (SZ1)                             |
| SZ1   | BLOB FOR NAME FILE                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #15: FILE DOWNLOAD REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0008h | NUMBER FOR FILE (SERVER)                             |
+-------+------------------------------------------------------+
```

### PACKET TYPE #16: FILE DOWNLOAD RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR FILE (SERVER)                             |
| 0008h | NUMBER FOR DOWNLOAD TRANSACTION                      |
+-------+------------------------------------------------------+
```

### PACKET TYPE #17: DOWNLOAD CHUNK REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR DOWNLOAD TRANSACTION                      |
| 0004h | NUMBER FOR CHUNK                                     |
+-------+------------------------------------------------------+
```

### PACKET TYPE #18: DOWNLOAD CHUNK RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR DOWNLOAD TRANSACTION                      |
| 0004h | NUMBER FOR CHUNK                                     |
| 0002h | LENGTH L1 OF CHUNK BLOB (SZ1 = L1 * 1)               |
| SZ1   | CHUNK BLOB (256 BYTES, LESS IF LAST ONE)             |
+-------+------------------------------------------------------+
```

### PACKET TYPE #15: FILE UPLOAD REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR SESSION                                   |
| 0004h | SIZE OF FILE                                         |
| 0002h | SIZE FOR NAME FILE (SZ1)                             |
| SZ1   | BLOB FOR NAME FILE                                   |
+-------+------------------------------------------------------+
```

### PACKET TYPE #16: FILE UPLOAD RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR FILE (SERVER)                             |
| 0008h | NUMBER FOR UPLOAD TRANSACTION                        |
+-------+------------------------------------------------------+
```

### PACKET TYPE #17: UPLOAD CHUNK REQUEST (CLIENT -> SERVER)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR UPLOAD TRANSACTION                        |
| 0004h | NUMBER FOR CHUNK                                     |
| 0002h | LENGTH L1 OF CHUNK BLOB (SZ1 = L1 * 1)               |
| SZ1   | CHUNK BLOB (256 BYTES, LESS IF LAST ONE)             |
+-------+------------------------------------------------------+
```

### PACKET TYPE #18: UPLOAD CHUNK RESPONSE (SERVER -> CLIENT)

```
+-------+------------------------------------------------------+
| SIZE  | DESCRIPTION                                          |
+-------+------------------------------------------------------+
| 0002h | PACKET TYPE                                          |
| 0008h | NUMBER FOR UPLOAD TRANSACTION                        |
| 0004h | NUMBER FOR CHUNK                                     |
+-------+------------------------------------------------------+
```
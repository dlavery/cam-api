# CAM API

## Summary
This project aims to provide a simple API to support a case/task management application.

The following utilities are also included:
* encrypt/decrypt; to encrypt a file at the record level
* ruleset; a basic rules engine.

## API
The API will expose functionality to create tasks. A background (cron) job will assign tasks to work queues. The API will expose an endpoint to draw the next task from the queue on a priority basis. It is intended to wrap auth (see the repo in this account) around the API to secure it. It is also intended that in the wild this API would be protected by a gateway such as Kong (http://getkong.org).

## Utilities

### encrypt/decrypt
The encrypt.py utility will generate a random symmetric key, encrypt a file named 'to-be-encrypted.csv' line by line to a file named 'encrypted.csv', and return the encryption key upon completion.

The decrypt.py utility requires an encryption key to be supplied in the command line and will decrypt the file 'encrypted.csv' to a file named 'decrypted.csv'.

Test files are included in this repo. No automated tests exist, manual testing was achieved by running encrypt/decrypt with the example 'to-be-encrypted' file and running a diff against the resultant, decrypted, file.

The utility was created as a test prior to developing the API's data handling capability.

### ruleset
A simplified rules engine based on a set of JSON-encoded rules and a 'when/then' pattern with support for 'and/or' clauses. The automated tests classify people into an age category based on a set of characteristics; a default category can be applied using a 'then' without a 'when'. The engine was created to assist with the assignment of tasks to work queues in the API.

The ruleset has features for more general use:
* Recursive conditional check meaning nested 'and' or 'or' clauses are supported
* Comparison operators [NULL, ALL, ANY, IN, EQ, LT, GT, LE, GE] are supported
* A 'then' clause without a 'when' can be used for default values.

The ruleset has the following drawback:
* The subject to which a ruleset applies must have a flat attribute structure, currently nested JSON objects are not supported
* Beware, when nesting, using the same JSON attribute twice within the same context (i.e. multiple 'and's or 'or's at the same level in the same 'when') - this causes addressing issues and inaccurate results.

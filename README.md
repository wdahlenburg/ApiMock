# ApiMock
Quickly mock up APIs through raw HTTP requests/responses to test front end validation. 

## How to use ApiMock

1. Create a folder for storing http requests and responses to store
2. Save the request/response pair with identical names in the folder. The request needs the extension .req and the response needs .resp.
3. If you are testing an application you don't host, modify your hosts file to set the back-end you are mocking to a local address. Otherwise configure your front-end application to point toward ApiMock.
4. Startup ApiMock by `python3 ./apimock.py -d testingDirectory`
5. Start to utilize the front-end application and you will see the mocked responses
6. The local files can be changed while the server is running so testing becomes easy. Just modify the response file and resend the request.

## Known Issues

- The server header is fixed in either the SimpleHTTPRequestHandler or BaseHTTPRequestHandler and the libraries don't like modifying this on the fly. 

## Progress

- Will be implmenting Strict mode so that the routing can be more exact. This will allow users to send GET and POST requests to the same endpoint and be able to mock different responses. This will be an option that can be selected.
- Clean up code
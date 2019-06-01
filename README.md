# ApiMock
Quickly mock up APIs through raw HTTP requests/responses to test front end validation. 

## How to use ApiMock

1. Create a folder for storing http requests and responses to store
2. Save the request/response pair with identical names in the folder. The request needs the extension .req and the response needs .resp.
3. If you are testing an application you don't host, modify your hosts file to set the back-end you are mocking to a local address. Otherwise configure your front-end application to point toward ApiMock.
4. Startup ApiMock by `python3 ./apimock.py -d testingDirectory`
5. Start to utilize the front-end application and you will see the mocked responses
6. The local files can be changed while the server is running so testing becomes easy. Just modify the response file and resend the request.

#### How to use ApiMock with TLS
1. Follow steps 1-3 from above
2. Create a root CA: `openssl genrsa -aes256 -out rootCA.key 2048`
3. Create the root certificate: `openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 365 -out rootCA.pem`
4. Fill out certficate.config with the correct alt_names. Ex: DNS.1 = mydomain.com
5. Create a certificate request for your site: `openssl req -new -nodes -out server.csr -newkey rsa:2048 -keyout server.key`
6. Create the certificate from the request in 4: `openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile certificate.config`
7. Add the Root CA as an authority certificate in your browser and allow it to identify websites.
8. `sudo python3 ./apimock.py -d test/ -tls=true -c server.crt -k server.key -p 443`
9. To verify visit https://myMockedDomain.com and ensure you don't get certificate errors. 

#### Options
| Argument      | Values           | Description  |
| ------------- |:-------------:| ------------:|
| -d / --directory     | * | Directory accessible by OS that stores the request and response pairs |
| -s / --server | Any IPv4 address owned by host | Server IP to host ApiMock |
| -p / --port | 0-65535 | Any port to run ApiMock on |
| -m / --mode | lax / strict | Mode to run for ApiMock. Lax mode only cares about the path. Strict mode supports http verb and path |
| -tls | true / false | Enable TLS |
| -k / --keyfile | server.key | PEM based server key for TLS |
| -c / --certificate | server.crt | PEM based certificate for TLS |

## Known Issues
- The server header is fixed in either the SimpleHTTPRequestHandler or BaseHTTPRequestHandler and the libraries don't like modifying this on the fly. 
import sys
import requests
#from bs4 import BeautifulSoup
import warnings
import os.path
import os
from glob import glob

###
#  Run it from Windows PyCharm

def main(argv):
    warnings.filterwarnings("ignore")
    hostname = ''
    username = ''
    password = ''
    version = ''
    #local_file_path = ''
    token = ''

    try:
        hostname = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
        version =  sys.argv[4]
        #version = "12.5"
        #local_file_path = sys.argv[4]
    except:
        print('Please enter hostname/IP Address, username, password, the local file path, and the remote file path')
        sys.exit()

    # convert local directoty + Files folder to String from List
    local_file_path = "".join(glob(str(os.getcwd()) + "\\Files"))



    #stop = input("stop")
    # Create a new session to maintain cookies across requests
    s = requests.Session()  # <requests.sessions.Session object at 0x103dbff98>

    # Post authentication details to authenticate cookie
    payload = {'appNav': 'cmplatform', 'j_username': username, 'j_password': password}


    #print(float(version))
    if float(version) >= 11:
        post = s.post('https://' + hostname + '/cmplatform/j_security_check', data=payload, verify=False)
        # print(post)

        # Initial Get Request to get a cookie
        getcookie = s.get('https://' + hostname + '/cmplatform', verify=False) # <Response [200]>

        # Get request to obtain first Struts Token, use Beautiful Soup to extract token from returned CSS
        tokenrequest = s.get('https://' + hostname + '/cmplatform/tftpFileUpload.do', verify=False)
        #print(tokenrequest)  # <Response [200]>
        soup = BeautifulSoup(tokenrequest.text)
        #print(soup)
        try:
            token = soup.find('input', {'name': 'token'}).get('value')  # 66S916ZIKZDYT292XRIUNE6PHFMQ0OZX

        except:
            print('Couldn''t get token.  You may be trying too often.')
            sys.exit()
    else:
        getcookie = s.get('https://' + hostname + '/cmplatform', verify=False)  # <Response [200]>
        post = s.post('https://' + hostname + '/cmplatform/WEB-INF/pages/j_security_check', data=payload, verify=False)
        #print(post.text)

    #stop = input("stop")



    # For Loops to walk through all files in directory/sub-directories
    for root, dirs, files in os.walk(local_file_path):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))

        for file in files:
            print(len(path) * '---', file)
            fullpath = os.path.join(root, file)
            remote_path = os.path.relpath(root, local_file_path)

            # Needed for Windows file paths
            remote_path = remote_path.replace("\\", "/")

            # Upload individual file
            f = open(fullpath, 'rb')


            if float(version) >= 11:
                # Post response will provide the next Struts token
                postfile = s.post('https://' + hostname + '/cmplatform/tftpFileUpload.do',
                                  files={'struts.token.name': (None, 'token'), 'token': (None, token),
                                         'file': (file, f, 'application/octet-stream'), 'directory': (None, remote_path)},
                                  verify=False)
                soup = BeautifulSoup(postfile.text)

                try:
                    token = soup.find('input', {'name': 'token'}).get('value') #update token for each run
                    #print(token)
                except:
                    print('Couldn''t get token.  You may be trying too often.')
                    sys.exit()
                #print('Uploaded file ' + file + ' to ' + remote_path)
                print('Uploaded file ' + file + ' to ' + hostname)

            else:
                req = requests.Request("POST", 'https://' + hostname + '/cmplatform/tftpFileUpload.do',
                                       files={'file': (file, f, 'application/octet-stream'),
                                              'directory': (None, remote_path)},
                                       cookies=s.cookies).prepare()
                postfile = s.send(req, stream=True, verify=False)
                print('Uploaded file ' + file + ' to ' + hostname)

                #print(postfile.text)

            f.close()


    print('\nBulk upload completed successfully!')

if __name__ == "__main__":
    main(sys.argv[1:])
Swift Video Store
===================================================

Contains a shell script to catch video, and a Python program to provide REST 
API for get post data and to pick the target videos to upload to Swift.


TODO
---------------------------------------------------
- fix potential bugs about timestamp processing
- gevent for multiple provessors in restapi
- ~~provide REST API ( Falcon )~~
- deal with exceptions 
- ~~use os module to handle system operations~~
- ~~config file~~
- swift functions applying
- optimize uploading
- tune ffmpeg to remove error messages
- add tests
- add doc by Sphinx


Requirements ( the env when dev )
---------------------------------------------------
ffmpeg
Python >= 2.7
Six >= 1.9
Falcon >= 0.2 
gevent >= 1.0.1
gunicorn >= 19.3.0
PyPy recommanded

Swift Video Store
===================================================

Contains a shell script to catch video, and a Python program to upload videos to swift


TODO
---------------------------------------------------
- provide REST API (by Django first, change to Falcon later) 
- deal with exceptions 
- use os module to handle system operations
- ~~config file~~
- swift functions applying
- optimize uploading
- tune ffmpeg to remove error messages
- add tests
- add doc by Sphinx


Requirements
---------------------------------------------------
Python >= 2.7
Six >= 1.9
PyPy
Falcon >= 0.2 
gevent >= 1.0.1
uWSGI >= 2.0.10

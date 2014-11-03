Private Files Directory
===

Files placed in this directory will be available through the file handler to anyone who is logged in and possesses the required rights.

Hidden files (filenames starting with a '.') are omitted and will not be sent out, unless the 'ALLOW_HIDDEN_FILES' option in 'bootstrap' is set to 'True'. This does NOT check for files hidden via the usual interface provided by the Windows platform, however preceding the filename with a '.' will still work on windows to prevent file access via the url/handler.
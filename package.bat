rd dist /s /q
pyinstaller -F xfm.py
copy settings.json dist
copy initpatch.json dist
xcopy images_animations\* dist\images_animations\ /cher
xcopy stipple\* dist\stipple\ /cher
copy README.mhtml dist
copy factory\* dist\factory\ /cher

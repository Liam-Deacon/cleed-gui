rem fix libpythonXX.a:
set python=python27
pexports %python%.dll > %python%.def
dlltool --dllname %python%.dll --def %python%.def --output-lib lib%python%.a 

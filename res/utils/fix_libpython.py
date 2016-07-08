# fix for bad reloc address issues when building C extensions 
import os
from shutil import copy2 as copy
import distutils.sysconfig

python_base = "python{}".format(distutils.sysconfig.get_python_version().replace(".", ""))
python_root = distutils.sysconfig.get_config_vars()['prefix']
python_libs = os.path.join(python_root, "libs")
python_dll = os.path.join(python_root, python_base + '.dll')
python_def = os.path.join(python_libs, python_base + '.def')

path = os.path.abspath(os.curdir)
pexports = os.path.join(path, "pexports.exe")

os.chdir(python_libs)
os.system("{exe} {dll} > {_def}".format(exe=pexports, dll=python_dll, _def=python_def))
copy(python_dll, python_dll + '.bak')
os.system("dlltool --dllname {dll} --def {_def} --output-lib lib{python}.a"
          "".format(dll=python_dll, _def=python_def, python=python_base)) 
os.chdir(path)
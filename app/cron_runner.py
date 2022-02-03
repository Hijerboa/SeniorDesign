# This is the runner used by the cron jobs. Don't use it for running your own scripts. You will be sad

import os
import sys
from pathlib import Path
from importlib import import_module
from importlib.util import find_spec

package_dir = os.path.join(str(Path(__file__).resolve().parent), 'cron_scripts')
module_name = sys.argv[1]
if os.path.isdir(os.path.join(package_dir, module_name)):
    try:
        # check if it's a python module
        if find_spec(f'cron_scripts.{module_name}.runner'):
            module = import_module(f'cron_scripts.{module_name}.runner')
            module.run()
    except:
        print(f'Could not load module {module_name}')
else:
    print(f'Could not find module {module_name}')

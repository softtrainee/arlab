

import os


beta = False if os.path.basename(os.path.dirname(__file__))=='pychron' else True
use_shared_memory = False

use_debug_logger = False

open_logger_on_launch = True

show_warnings = False
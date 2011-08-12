

import os
beta = True if 'beta' in os.path.basename(os.path.dirname(__file__)) else False
use_shared_memory = False

use_debug_logger = False

open_logger_on_launch = True

show_warnings = False
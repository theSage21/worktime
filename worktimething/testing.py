import time
from . import core


d = 1595311625.9705195 - 1595306529.1317801
assert core.to_jira(d) == "1h 24m"

from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='CloudFlare',
    icon='cloud',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import backend
    import main
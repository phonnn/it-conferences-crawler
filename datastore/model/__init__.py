from .Conference import *
from .ConferenceSource import *
from .ConferenceTopic import *
from .Source import *
from .Topic import *

tables = {
    'Conference': Conference,
    'Topic': Topic,
    'Source': Source,
    'ConferenceTopic': ConferenceTopic,
    'ConferenceSource': ConferenceSource
}
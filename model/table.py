from model.Conference import Conference
from model.ConferenceSource import ConferenceSource
from model.ConferenceTopic import ConferenceTopic
from model.Source import Source
from model.Topic import Topic

tables = {
    'Conference': Conference,
    'Topic': Topic,
    'Source': Source,
    'ConferenceTopic': ConferenceTopic,
    'ConferenceSource': ConferenceSource
}
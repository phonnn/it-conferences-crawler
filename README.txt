https://www.gartner.com/en/conferences/calendar
https://www.gartner.com/en/conferences/some-url
https://www.gartner.com/en/conferences/some-url/speakers


https://conference-api.ieee.org/conf/searchfacet?q=*&subsequent_q=&date=all&from=&to=&region=all&country=all&pos=0&sortorder=asc&sponsor=&sponsor_type=all&state=all&field_of_interest=all&sortfield=dates&searchmode=basic&virtualConfReadOnly=N&eventformat=
change pos in query
 - name
 - date
 - location
 - topic
 - description
 - website
 - sourceId


https://www.conferencelists.org/engineering-and-technology/page/1/
 - name
 - date
 - location
 - sourceId/sourceUrl

 - topic
 - description
 - website



https://www.acm.org/upcoming-conferences
 - name
 - date
 - location
 - website
 - sourceId


Conference(id, name, location, start_date, end_date, website, description)
Topic(id, name)
Source(id, name)
ConferenceTopic(conference_id, topic_id)

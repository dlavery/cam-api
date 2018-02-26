curl -X POST -H "Content-Type: application/json" -d '{"title": "news", "description": "check the news", "url": "http://bbc.co.uk/", "origin": "north", "tags": "news", "notbefore": "2018-12-25", "priority": "high"}' http://localhost:5001/tasks

curl http://localhost:5001/tasks/5a915d2998b2460db9391970

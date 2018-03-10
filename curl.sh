curl -X POST -H "Content-Type: application/json" -d '{"title": "news", "description": "check the news", "url": "http://bbc.co.uk/", "origin": "north", "tags": "news", "notbefore": "2018-12-25", "priority": "high"}' http://localhost:5001/tasks

curl http://localhost:5001/tasks/5a915d2998b2460db9391970

curl -X PUT -H "Content-Type: application/json" -d '{"notbefore": "2018-12-25", "priority": "medium", "note": {"text": "do not open before christmas", "originator": "dlavery"}}' http://localhost:5001/tasks/requeue/5a99a53098b246434138088f

curl -X PUT -H "Content-Type: application/json" -d '{}' http://localhost:5001/tasks/complete/5a99a53098b246434138088f

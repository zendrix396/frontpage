# TODO
-> buy sell functionality (done)
-> celery integration in database (done)
-> unrealized/realized gain
-> sell stock option
-> user profile on '/'
# bug: if already created email being given to sign up
## celery setup commands: 
```bash
# terminal 1
redis-server
# celery server
celery -A frontpage worker --pool=solo -l DEBUG
# celery beat
celery -A frontpage beat -l info
```
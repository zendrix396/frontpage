# TODO
* buy sell functionality (done ✅) 
*  celery integration in database (done ✅)
* unrealized/realized gain (done ✅)
* sell stock option (done ✅)
* user profile on '/' (done ✅)
* optimizing database, adding last_price to redis and dynamically updating database **in reference to lastprice** rather than pushing information real time [ongoing ⌛]
### bug: if already created email being given to sign up [fixed] ✅
## celery setup commands: 
```bash
# terminal 1
redis-server
# celery server
celery -A frontpage worker --pool=solo -l DEBUG
# celery beat
celery -A frontpage beat -l info
```

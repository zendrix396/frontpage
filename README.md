## TODO
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

## FUTURE Expansion
* optimize the real time functionality to scale it for a larger users pool (current realtime fetching is pretty shitty)
* add limited time block (for prod)=> where the market is open (9:15 to 3:30) monday to friday
* add the ai [[ML]] bot that will have it's own portfolio (publically available) along with previous history of trading (keep enhancing it such that it outperforms and do well)


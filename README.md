# CPA-OPEN

Deploy on Railway in 2 minutes:

1. git clone your repo
2. Railway new project -> Python -> Connect Git
3. Add env vars: TARGET_URL, REDIS_URL (free Redis on Railway), DB_URL=sqlite:///
4. Deploy web + worker processes (2-4 workers)
5. Done. Bot runs 24/7, clicks every 12s, 10% test mode.



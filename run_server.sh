pip install flask pandas psycopg2 requests flask_cors
docker-compose up -d 
docker cp modules/schema.sql weatherapp_database_1:/
docker exec -it weatherapp_database_1 psql -U postgres -f schema.sql
export FLASK_APP=server.py
export FLASK_ENV=development
export FLASK_DEBUG=True
apt-get install nohup
nohup flask run > log.txt  2>&1 &
python cron.py
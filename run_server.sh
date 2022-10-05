pip install flask pandas psycopg2 requests flask_cors
docker-compose up -d 
docker cp modules/schema.sql weatherapp_database_1:/
docker exec -it weatherapp_database_1 psql -U postgres -f schema.sql
expose FLASK_APP=server.py
expose FLASK_ENV=development
expose FLASK_DEBUG=True
apt-get install nohup
nohup flask run > log.txt  2>&1 &
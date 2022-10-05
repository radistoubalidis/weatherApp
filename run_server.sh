pip install flask pandas psycopg2 requests flask_cors
docker-compose up -d 
docker cp modules/schema.sql weatherapp_database_1:/
docker exec -it weatherapp_database_1 psql -U postgres -f schema.sql
sudo export FLASK_APP=server.py
sudo export FLASK_ENV=development
sudo export FLASK_DEBUG=True
sudo apt-get install nohup
sudo nohup flask run > log.txt  2>&1 &
python cron.py
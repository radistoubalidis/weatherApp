pip install flask pandas psycopg2 requests flask_cors
docker-compose up -d 
docker cp modules/schema.sql weatherapp_database_1:/
docker exec -it weatherapp_database_1 psql -U postgres -f schema.sql
bash -c "export FLASK_APP=server.py"
bash -c "export FLASK_ENV=development"
bash -c export FLASK_DEBUG=True
sudo apt-get install nohup
sudo nohup flask run > log.txt  2>&1 &
python cron.py
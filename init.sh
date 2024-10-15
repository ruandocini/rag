export $(cat .env | xargs)
cd db
docker-compose build
docker-compose up -d
cd ..
uvicorn main:app --reload
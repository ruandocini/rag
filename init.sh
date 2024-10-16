conda create -n rag-system python=3.8 -y
source activate base
conda init
conda activate rag-system
pip install -r requirements.txt
export $(cat .env | xargs)
cd db
docker-compose build
docker-compose up -d
cd ..
uvicorn main:app --reload
sudo apt install postgresql -y
pip install -r requirements.txt
createdb -U nicocaramel protorhapi
psql -U nicocaramel -d protorhapi -a -f database_rh.psql

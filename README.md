```
python3 -m venv venv
python3 -m pip install -r requirements.txt
```
![alt text](https://media.tenor.com/5lLcKZgmIhgAAAAC/american-psycho-patrick-bateman.gif)

Также, необходимо установить `exiftool` (удаление метаданных происходит в файле `dip/utils/security.py` 
посредством исполнения `shell`-команды)

```
export FLASK_APP=dip
flask db init
flask db migrate
flask run
```

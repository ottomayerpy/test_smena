# test_smena

Использовал **curl 7.68.0**, **python 3.8.10**, **pip 20.0.2**.

## Инициализация

```bash
git clone https://github.com/ottomayerpy/test_smena
cd test_smena
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 manage.py runserver
```
Прежде чем запустить Django, запускаем контейнеры:
```bash
docker-compose up
```
После загрузки контейнеров запускаем rq:
```bash
python3 manage.py rq_worker
```

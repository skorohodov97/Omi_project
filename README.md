1. С чего начать:
   

* установить приложения Gadgetbridge и Omi на Android
* подключить кольцо Colmi R10 к Gadgetbridge, носимое устройство (кулон) - к приложению Omi.
* Проанализировать возможности, интерфейс, ограничения и недостатки



2\. Первый этап проекта:

Цель - обеспечить передачу "сырых" данных с устройств с носимых устройств Omi и колец Colmi R10
на собственный сервер.

ПО:

* Создать репозиторий GitHub (закрытый), добавить меня с правами правки кода
* С устройства Omi через приложение Android и собственный webhook предаем байтовый поток с преобразованием в Wav.



https://docs.omi.me/doc/developer/AudioStreaming#real-time-audio-streaming



* C кольца через Gadgetbridge передаем данные о психофизиологических показателях (формат уточнить в ходе эксперимента)



Железо:

* Паяем 30 устройств Omi
* Печатаем 30 корпусов на 3D принтере
* Собираем тестовую партию



3\. Второй этап проекта:

Цель: Добиться того, чтобы вся функциональность по передаче данных на свой сервер содержалась в одном 
приложении Android



Варианты:

* подключить Omi через Gadgetbridge
* Разработать собственное приложение Android




Имеющийся задел:
см. папку Omi\_Project



запуск сервера через Poetry выполняется командой:



poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug





cloudflared tunnel --url http://localhost:8000 --protocol http2


Утстановка окружения:
pip install -r requirements.txt


Обновление на сервере:
git fetch origin
git reset --hard origin/main
poetry install --no-root
sudo systemctl restart omi-backend.service




# DS-RL-Master

Build docker image:

> docker build . -t master-service:lstest

To run image:

> dorker run -p 30000:30000 master-service:lstest


## ІТЕРАЦІЯ 2 

>Current iteration should provide tunable semi-synchronicity for replication, by defining write concern parameters. <br />
> - client POST request in addition to the message should also contain write concern parameter w=1,2,3,..,n <br />
> - w value specifies how many ACKs the master should receive from secondaries before responding to the client <br />
> w = 1 - only from master <br />
> w = 2 - from master and one secondary <br />
> w = 3 - from master and two secondaries <br />

У клас MasterService з ``MasterService.py`` було внесено можливість зчитувати параметр ``write-concern``:
<img width="676" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/609846c6-a189-42ad-8ab3-273cd622f359">

- Перевірка при w = 1: 

Бачимо, що відповідь клієнту прийшла за 1 секунду, в той час в логах секондарі отримали POST лише через декілька секунд:
<img width="1000" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/62b91b2e-718f-47b9-840c-3ed3c83073ed">
<img width="661" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/590667d0-8c3f-42f2-a443-af024d249626">

Вміст повідомлення успішно отримується через GET до secondary-1:
<img width="1033" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/585e1220-3f7b-4aa6-becb-e23786641e72">

- Перевірка при w = 2:
<img width="1007" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/45093411-ab0b-4d23-bbba-9d4bc97457a1">
<img width="655" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/0a775667-fc13-4438-9b72-031b2d0d1907">

Вміст повідомлення успішно отримується через GET до secondary-1:
<img width="1004" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/c517d12d-549f-4d9a-8dcc-4050e740652e">


- Перевірка при w = 3:
Додавання очікування на ACK від secondary-2-1 збільшило час очікування до кількох секунд: 
<img width="1035" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/ff73ee2a-abf8-4321-918d-eeaa142cc591">
<img width="657" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/5ea181f5-ecf9-440e-9443-89a04573161a">

Вміст повідомлення успішно отримується через GET до secondary-1 (20000) та laggy-secondary-1 (20001):
<img width="987" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/6ccbe1a4-7f89-4d89-8c26-66fbacbf83a5">
<img width="1014" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/0b10047f-3b13-4c97-89fb-e656045d51a2">


>Please emulate replicas inconsistency (and eventual consistency) with the master by introducing the artificial delay on the secondary node. In this case, the master and secondary should temporarily return different messages lists.

Введемо штучну затримку 30 секунд для secondary-1 та 60 секунд для laggy-secondary-1, модифікуючи ``compose.yaml``
<img width="307" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/5d63c285-022c-47ef-91e3-d789504e7b5d">
<img width="301" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/e4d62673-f34d-4b01-96cd-db0d675c8535">

- Перевірка при w = 1:
Надсилаємо POST на master-1, отримуємо статус-код 200 (OK) від мастера, але при зверненні через GET до laggy-secondary-1 (20001) ми отримуємо пусте тіло:
<img width="1044" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/05f85aa1-36db-4649-b147-a499e132e5fd">
<img width="1014" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/56c74399-f1b2-4828-9c4e-11ff05610856">

У логах бачимо, шо повідомлення прийшло на laggy-secondary-11 із затримкою, а GET-запит було отримано master-1 до того, як повідомленя POST прийшло на laggy-secondary1
<img width="840" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/77794eb1-adf3-4d72-afc4-fe1c0e0c5ab2">

Через 60 секунд повідомлення успішно отримується від laggy-secondary-1:
<img width="999" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/2887f0b4-dcc4-4ee7-94c5-65e15371c75e">

Перевірка при w = 3: 
Надсилаємо POST на master-1, отримуємо статус-код 200 (OK) від мастера через 30+ секунд:
<img width="1013" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/87360b78-f2fb-4d92-b2e8-926a2f8ca9d6">





>Add logic for messages deduplication and to guarantee the total ordering of messages.

Завдяки індексації повідомлень, повідомленням з однаковим контентом присвоюються відмінні почергові індекси:
<img width="1080" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/2c63b6b7-9859-4c10-b567-c0a42931d3b0">

Це реалізовується за допомогою інстансу класу MasterDomain, котрий викликає функцію domain_log під час виконання функції add_message:

<img width="491" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/171d7f90-9b17-4da0-8413-301e9f04d297">

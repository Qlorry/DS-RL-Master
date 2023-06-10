# DS-RL-Master

Build docker image:

> docker build . -t master-service:lstest

To run image:

> dorker run -p 30000:30000 master-service:lstest


## ІТЕРАЦІЯ 3

> Для імплементації не блокуючого очікування нод для задоволення concern level, прийшлось використати інший вебсервер для Мастера з нативною підтримкою asyncio та корутин. 
Було додано логіку 

he current iteration should provide tunable semi-synchronicity for replication with a retry mechanism that should deliver all messages exactly-once in total order.

Main features:
1. If message delivery fails (due to connection, or internal server error, or secondary is unavailable) the delivery attempts should be repeated - retry

>Було додано аргумент в мастер контролюючий retry mechanism. Без додаткової логіки для інтервалів часу між retry, константний час.

Продемонструємо додавши faulty-secondary в компоуз файл
![Alt text](img/retry2.png?raw=true) 
Відправимо ще кілька повідомлень, і перевіримо faulty-secondary, всі повідомлення є
![Alt text](img/retry1.png?raw=true) 

 - If one of the secondaries is down and w=3, the client should be blocked until the node becomes available. Clients running in parallel shouldn’t be blocked by the blocked one.  
 
 > З вебсервером Tornado це стало можливим, мастер буде очікувати достатню кількість нод скільки потрібно

 - If w>1 the client should be blocked until the message will be delivered to all secondaries required by the write concern level. Clients running in parallel shouldn’t be blocked by the blocked one.  

 > Завдяки корутинам паралельні клієнти не блокують одне одного очікуючи на результат виклику, достатню кількість ACK чи нод для concern level. 
 > Цю логіку буде продемонстровано в кінці, пункт 4 та 10. 

 - All messages that secondaries have missed due to unavailability should be replicated after (re)joining the master

> Функція реєстрації вісилає актуальний набір повідомлень. 

 - Retries can be implemented with an unlimited number of attempts but, possibly, with some “smart” delays logic

> Ліміт задається аргументом на мастері


2. All messages should be present exactly once in the secondary log - deduplication
- To test deduplication you can generate some random internal server error response from the secondary after the message has been added to the log
3. The order of messages should be the same in all nodes - total order
 - If secondary has received messages [msg1, msg2, msg4], it shouldn’t display the message ‘msg4’ until the ‘msg3’ will be received
 - To test the total order, you can generate some random internal server error response from the secondaries

> Повідомлення зберігаються в мастері та секондарі в структурі dict, за унікальними ідентифікаторами. Ця структура не надає сортування, тому в доменній логіці в функціях get_messages наявне сортування за індексами. Таким чином не буде дуплікатів, а порядок буде такий як порядок надходження повідомлень в мастер(там вони додаються з песимістичним блокуванням)

### Продемонструємо цей механізм за алгоритмом:

> 1. Start M + S1  
> 1. send (Msg1, W=1) - Ok   
> 1. send (Msg2, W=2) - Ok   
> 1. send (Msg3, W=3) - Wait   
> 1. get from Master -> Msg1, Msg2, Msg3  
> 1. get from Secondary -> Msg1, Msg2  
> 1. send (Msg4, W=1) - Ok   
> 1. get from Master -> Msg1, Msg2, Msg3, Msg4  
> 1. get from Secondary -> Msg1, Msg2  
> 1. Start S2   
> 1. Check messages on S1 - [Msg1, Msg2, Msg3, Msg4]   
> 1. get from Secondary 2 -> Msg1, Msg2, Msg3, Msg4

Логи:

1. Запуск
    ![Alt text](img/1.png?raw=true)  
1. Перше повідомлення
    ![Alt text](img/2.png?raw=true)  
1. Друге повідомлення
    ![Alt text](img/3.png?raw=true)  
    ![Alt text](img/3.1.png?raw=true)  
1. Третє повідомлення
    ![Alt text](img/4.png?raw=true)  
    ![Alt text](img/4.1.png?raw=true)  
1. Get Messages з Мастера
    ![Alt text](img/5.png?raw=true)  
1. Get Messages з Секондарі
    ![Alt text](img/6.png?raw=true)  
1. Четверте повідомлення
    ![Alt text](img/7.png?raw=true)  
    ![Alt text](img/7.1.png?raw=true)  
1. Get Messages з Мастера
    ![Alt text](img/8.png?raw=true)  
1. Get Messages з Секондарі
    ![Alt text](img/9.png?raw=true)  
1. Запуск другого секондарі
    ![Alt text](img/10.png?raw=true)  
    Завершується відпаравка 3го повідомлення.(див час обробки)
    ![Alt text](img/10.1.png?raw=true) 
1. Get Messages з Першого Секондарі
    ![Alt text](img/11.png?raw=true)  
1. Get Messages з другого Секондарі
    ![Alt text](img/12.png?raw=true)  



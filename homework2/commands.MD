Скачиваем docker-контейнер с hive-сервером:
```commandline
git clone https://github.com/dertty/apache-spark-docker.git
cd apache-spark-docker/docker
docker-compose up -d
```
Проверить, что все 12 контейнеров docker стартовали, можно в Docker UI. При необходимости - остановить другие контейнеры, освободить порты. Либо установить другие порты в docker-compose.yaml.

Заходим в hdfs файловую систему контейнера
Запускает интерактивную сессию в docker-контейнере с именем hive-server, где лежит командная строка для работы с hive. Beeline - клиентская командная строка для работы с hive.
Указывает клиентской командной строке, что нужно подключиться к hive-серверу, используя jdbc-подключение к БД, в которой работают hql-запросы.
```commandline
docker exec -it hive-server beeline -u 'jdbc:hive2://hive-server:10000/'
```
В результате команды должны попасть в "0: jdbc:hive2://hive-server:10000/>", а не в "beeline".
Если попадаем в "beeline", то нужно попробовать поперезапускать hive-server, и подождать между перезапуском hive-сервера и выполнением этой команды.

Откроем еще один терминал.
Скопируем файл .csv с локального хранилища в docker-контейнер.
```commandline
cd apache-spark-docker/docker
docker cp AB_NYC_2019.csv namenode:/tmp
```
Теперь файл лежит в самом docker-контейнере и необходимо переместить его в hdfs файловую систему hadoop-кластера.
Зайдем в контейнер namenode.
```commandline
docker exec -it namenode /bin/bash
```
Здесь начинает работать синтаксис hdfs.
```commandline
hdfs dfs -put /tmp/AB_NYC_2019.csv /
```
Если здесь возникает ошибка типа
```
hdfs://namenode:8020/AB_NYC_2019.csv._COPYING_
put: Cannot create file/AB_NYC_2019.csv._COPYING_. Name node is in safe mode.
```
, то можно выйти из безопасного режима:
```commandline
hdfs dfsadmin -safemode leave
hdfs dfs -put /tmp/AB_NYC_2019.csv /
```
Если на этом этапе нода namenode падает, то можно отключить все ноды docker контейнера кроме namenode, datanode1, datanode2.

Теперь файл лежит на самом hdfs и hive сможет его увидеть.

Возвращаемся в первый терминал.
```commandline
CREATE TABLE `aibnb` (`id` int, `name` string, `host_id`
int, `host_name` string, `neighbourhood_group` string, `neighbourhood` string,
`latitude` float, `longtitude` float, `room_type` string,
`price` float, `minimum_nights` int, `number_of_reviews` int, `last_review` date, `reviews_per_month` float, `calculated_host_listings_count` int, `availability_365` int) row format delimited fields terminated by ',' stored as textfile;
select * from artists;
```
Загружаем данные из файла в таблицу.
```commandline
load data inpath '/AB_NYC_2019.csv' into table aibnb;
select * from artists limit 5;
```
Посчитаем среднее значение и дисперсию цены.
```commandline
SELECT AVG(price) FROM aibnb;
SELECT VARIANCE(price) FROM aibnb;
```

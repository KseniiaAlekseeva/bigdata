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

Работает аналогично sql-запросам.
```commandline
show tables;
create table test(a string, b int);
show tables;
select * from test;
create table test(a string, b int) partitioned by (c int);
insert into a partition (c=1) values ('a',1),('a',2),('b',3);
select * from a;
```
Откроем еще один терминал.
Скопируем файл .csv с локального хранилища в docker-контейнер.
```commandline
cd apache-spark-docker/docker
docker cp artists.csv namenode:/tmp
```
Теперь файл лежит в самом docker-контейнере и необходимо переместить его в hdfs файловую систему hadoop-кластера.
Зайдем в контейнер namenode.
```commandline
docker exec -it namenode /bin/bash
```
Здесь начинает работать синтаксис hdfs.
```commandline
hdfs dfs -put /tmp/artists.csv /
```
Если здесь возникает ошибка типа
```
hdfs://namenode:8020/artists_mini.csv._COPYING_
put: Cannot create file/artists_mini.csv._COPYING_. Name node is in safe mode.
```
, то можно выйти из безопасного режима:
```commandline
hdfs dfsadmin -safemode leave
hdfs dfs -put /tmp/artists.csv /
```
Если на этом этапе нода namenode падает, то можно отключить все ноды docker контейнера кроме namenode, datanode1, datanode2.

Теперь файл лежит на самом hdfs и hive сможет его увидеть.

Возвращаемся в первый терминал.
```commandline
CREATE TABLE `artists` (`mbid` string, `artist_mb` string, `artist_lastfm`
string, `country_mb` string, `country_lastfm` string, `tags_mb` string,
`tags_lastfm` string, `listeners_lastfm` int, `scrobbles_lastfm` int,
`ambiguous_artist` boolean) row format delimited fields terminated by ',' stored as textfile;
select * from artists;
```
Загружаем данные из файла в таблицу.
```commandline
load data inpath '/artists.csv' into table artists;
select * from artists limit 5;
```
Выведем артистов с максимальным количеством scroblов.
```commandline
SELECT artist_mb, MAX(scrobbles_lastfm) max FROM artists GROUP BY artist_mb ORDER BY max DESC LIMIT 5;
```
Если команда не выполняется и hive-сервер падает, то нужно уменьшить файл, чтобы он влезал в один блок памяти (128 Мб).
Посчитаем количество строк в файле.
```commandline
wc -l artists.csv
```
Разобьем файл на несколько по числу строк.
```commandline
split -l 100000 artists.csv
```

```commandline
SELECT trim(itemsName) tag_lastfm, count(*) cnt from artists lateral view explode(split(tags_lastfm, ';')) itemTable AS itemsName group by trim(itemsName) order by cnt desc limit 5;
```


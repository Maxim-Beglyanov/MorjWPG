## Как задеплоить бота
На данный момент бота необходимо ставить самому, он является ботом для одного сервера. Я рассмотрю случай деплоя для [Heroku](https://heroku.com)

### Ресурсы
Следующие ресурсы помогут вам в деплое бота

Деплой бота:
- https://www.youtube.com/watch?v=TtvNVDilh60&t=58s&ab_channel=%D0%A5%D0%B0%D1%83%D0%B4%D0%B8%D0%A5%D0%BE%E2%84%A2-%D0%9F%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%BE%D0%BC%D0%B8%D1%80%D0%B5IT%21
- https://www.youtube.com/watch?v=9bJgcikmfHI&t=315s&ab_channel=PyLounge-%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%D0%BD%D0%B0Python%D0%B8%D0%B2%D1%81%D1%91%D0%BEIT

Heroku CLI:
- https://www.youtube.com/watch?v=fpEgZi3_RI4&ab_channel=Fraser
- https://www.youtube.com/watch?v=3eep8apTnGA&ab_channel=CodeJava

1. Зарегистрируйтесь на Heroku, для этого вам нужна будет почта, на данный момент хостинг не принимает Российские и Белорусские почты, поэтому создайте с Английским регионом или с любым другим
2. Создайте проект в dashboard Heroku
После создания аккаунта вы попадете в dashboard, в нем вам необходимо создать новый проект
![Screenshot_20220516_193012](https://user-images.githubusercontent.com/58074318/168592909-7210cab7-4bd2-4027-bede-3e91bb318297.png)

После нажатия кнопки create new app, назовите ваш проект и выберите место, где будет сервер(в Америке или Европе)
![Screenshot_20220516_193321](https://user-images.githubusercontent.com/58074318/168593260-20e3e2bf-00bf-4811-a18f-bfdb5f97ec99.png)
3. Подключите базу данных Postgres
После создания нового проекта вы попадете на страницу управления им. Здесь вам необходимо перейти в раздел Resources и нашать кнопку Find More add-ons
![Screenshot_20220516_194505](https://user-images.githubusercontent.com/58074318/168595365-dc09edf0-b2d2-4e44-af50-b53e5933445d.png)

Вы попадаете на страницу add-ons, здесь вам надо найти дополнение Heroku Postgres, нажмите на него. А на следующей страницу нажмите кнопку Install Heroku Postgres
![Screenshot_20220516_194648](https://user-images.githubusercontent.com/58074318/168595724-a4a3a9b2-d8e4-47ea-a01b-4ef2f0af9a02.png)
![Screenshot_20220516_194755](https://user-images.githubusercontent.com/58074318/168595954-04f546a5-ecdf-4990-a9b4-4a5612c6a5ad.png)

На странице подключения Postgres выберите план Hobby Dev - Free(указан по умолчанию) и напише в поле App to provision to имя вашего проекта, а затем выберите его. После нажмите на кнопку Submit Order Form
![Screenshot_20220516_195419](https://user-images.githubusercontent.com/58074318/168597076-a4c30aad-83d7-4e26-b036-572b1ce57be8.png)
![Screenshot_20220516_195442](https://user-images.githubusercontent.com/58074318/168597193-ff99bdd5-aef4-4c14-b97b-5835dfbca0fe.png)
3. Загрузите код бота на Heroku
После добавления базы данных в проект вам необходимо перейти в раздел Deploy и выбрать Heroku Git(на данный момент добавление проекта гитхаба в Heroku не работает) и установить Heroku CLI
![Screenshot_20220516_200303](https://user-images.githubusercontent.com/58074318/168598747-d5c414ec-7c3f-4dbd-8ecc-8ee3e2a06507.png)

После установки Heroku CLI в нем необходимо прописать команды `heroku login`, после чего вас перебросит на сайт, где пройдет регистрация в Heroku CLI

Далее вы должны скачать проект и загрузить файлы в папку, вам надо будет переместиться в эту папку через консоль после чего прописать следующие команды `git init` и `heroku git:remote -a название-вашего-проекта-на-хероку`

Потом для работы скрипта необходимо перейти в категорию Settings и нажать кнопку Reveal Config Vars
![Screenshot_20220516_201342](https://user-images.githubusercontent.com/58074318/168600664-844f72e1-9aa4-4876-b9b1-18e82fe36f72.png)

У вас раскроются подробности переменных, где вам надо будет добавить новую переменную. В поле Key впишите "DISCORD_TOKEN", а в поле Value напротив токен вашего бота. Далее нажмите на кнопку Add
![Screenshot_20220516_201544](https://user-images.githubusercontent.com/58074318/168601075-cf0c9266-df67-4fbf-83b4-950177791463.png)

4. Запуск бота
После загрузки кода в категории Resources появится worker с переключателем. Вам необходимо нажать на карандаш, а после активировать переключатель и нажать Confirm
![Screenshot_20220516_201845](https://user-images.githubusercontent.com/58074318/168601629-35180fad-d703-4765-9ade-34f271ff4f4a.png)

Бот запущен, поздравляю

5. Обновления бота
Тк бот будет обновляться и улучшаться функционал. Вам необходимо будет обновлять своего бота
Для этого вы должны перейти в папку с помощью которой вы загружали бота с помощью консоли и перенести файлы новой версии с заменой старых, после выполните команду `git commit -am "make it better"`, а затем `git push heroku master`

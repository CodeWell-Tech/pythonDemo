# flask-blog
A simple blog web project, use python-flask.

## run
### install dep and env
	> install at global or virtualenv
	```
    pip install  -r ./requirements.txt
    ```
### create db
	```
    python ./db_migrate.py
    ```
	
### run 
	`server: `
	```
    python ./run.py
    ```
	> default: Running on http://127.0.0.1:5000/
	
	`browser:`
	```
	http://127.0.0.1:5000/
	```

## feature
	- sign in 
	  login  
	  logout
	  avatar
	  micro-blog
	  follow/unfollow
	  user profile
	
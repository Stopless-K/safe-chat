all:
	@
server:
	python3 server.py
client:
	python3 client.py

push:
	git add * &
	sleep 1
	git status
	git commit -m 'updated'
	git push origin master

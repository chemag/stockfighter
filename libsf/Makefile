all: example


example:
	# start server
	@echo "---------- server.py"; \
	{ ./server.py & }; \
	pid="$$!"; \
	sleep 2; \
	echo "---------- client.py -d"; \
	./client.py -d; \
	ret=$$?; \
	sleep 1; \
	kill $$pid; \
	echo ""; \
	exit $$ret


database.sqlite: schema.sql
	sqlite3 database.sqlite < schema.sql


clean:
	rm -rf *.pyc

realclean:
	rm -rf database.sqlite

save:
	rsync -avut --progress ./ creolina:projects/stockfighter/


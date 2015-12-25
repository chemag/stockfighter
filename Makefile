
all: sync

sync:
	rsync -avut --progress ./ creolina:projects/stockfighter/

reverse:
	rsync -avut --progress creolina:projects/stockfighter/ ./

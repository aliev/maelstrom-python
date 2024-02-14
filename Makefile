include .env

test-echo:
	${MAELSTROM_BIN_PATH}/maelstrom test -w echo --bin $(shell which mnode) --time-limit 5 --log-stderr

test-broadcast:
	${MAELSTROM_BIN_PATH}/maelstrom test -w broadcast --bin $(shell which mnode) --time-limit 20 --rate 100 --node-count 25 --topology line --latency 100

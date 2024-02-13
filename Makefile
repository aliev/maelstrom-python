include .env

test-echo:
	${MAELSTROM_BIN_PATH}/maelstrom test -w echo --bin ./node --time-limit 5 --log-stderr

test-broadcast:
	${MAELSTROM_BIN_PATH}/maelstrom test -w broadcast --bin ./node --time-limit 5 --rate 10 --log-stderr

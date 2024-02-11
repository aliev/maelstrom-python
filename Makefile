include .env

test-echo:
	${MAELSTROM_BIN_PATH}/maelstrom test -w echo --bin ./node --time-limit 5 --log-stderr

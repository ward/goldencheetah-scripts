all: output/training-log.html output/rolling-total.html output/distance-histogram.html

rideDB.json: ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json
	cp ~/.goldencheetah/Ward\ Muylaert/cache/rideDB.json .

output/training-log.html: training-log.py rideDB.json
	python training-log.py

output/rolling-total.html: rolling-total.py rideDB.json
	python rolling-total.py

output/distance-histogram.html: distance-histogram.py rideDB.json
	python distance-histogram.py

sync: all
	rsync --progress output/*.html vps:/var/www/run.wxm.be/graphs/

clean:
	rm rideDB.json
	rm -r output/

ifeq ($(VERBOSE),1)
    SILENT=
else
    SILENT=@
endif

all:
	$(SILENT)python3 server.py > /dev/null 2>&1 &
	$(SILENT)python3 IPCamerasFramework.py > /dev/null 2>&1 &
	@echo "Go to http://127.0.0.1:5000 for login page"
	
clean:
	$(SILENT)pkill -f 'server.py'
	$(SILENT)pkill -f 'IPCamerasFramework.py'
	@echo "Killed the processes for the server and client(s)"

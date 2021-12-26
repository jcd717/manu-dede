#!/bin/sh

export SECRET_KEY=$(python -c "import string,random; print(''.join(random.choice(string.ascii_letters+string.digits+'-_:./+%£') for i in range(32)))")
flask init-db 
flask reload-downloads
rm run-init.sh
mv run-restart.sh run-init.sh
exec flask run -h 0.0.0.0 -p $PORT


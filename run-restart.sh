#!/bin/sh

export SECRET_KEY=$(python -c "import string,random; print(''.join(random.choice(string.ascii_letters+string.digits+'-_:./+%£') for i in range(32)))")
flask reload-downloads
exec flask run -h 0.0.0.0 -p $PORT

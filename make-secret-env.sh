#!/bin/sh

echo SECRET_KEY=$(python -c "import string,random; print(''.join(random.choice(string.ascii_letters+string.digits+'-_:./+%£') for i in range(32)))") > secret.env

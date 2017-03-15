#!/bin/sh

B=`pwd`
until buildbot upgrade-master $B
do
    echo "Can't upgrade master yet. Waiting for database ready?"
    sleep 1
done
exec twistd -ny $B/buildbot.tac

#!/bin/bash
ps auxww | grep 'celery worker' | awk '{print $2}'

import swiftclient.client

def bucketfilelinegen(swiftconnection, bucketname, filename, chunksize = 1024*1024):
    (obj_header, obj_body) = swiftconnection.get_object(bucketname, filename, resp_chunk_size=chunksize)
    linerem = ''
    for chunk in obj_body:
        first = True
        for s in chunk.split('\n'):
            if first:
                first = False
            else:
                yield linerem
                linerem = ''
            linerem += s

def bucketfilelinecount(swiftconnection, bucketname, filename, chunksize = 1024*1024):
    linecount = 0
    for line in bucketfilelinegen(swiftconnection, bucketname, filename, chunksize):
        linecount += 1
    return linecount

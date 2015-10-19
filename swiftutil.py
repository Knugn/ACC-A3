import swiftclient.client

def bucketfilelinegen(swiftconnection, bucketname, filename, chunksize = 1024*1024):
    (obj_header, obj_body) = swiftconnection.get_object(bucketname, filename, resp_chunk_size=chunksize)
    for chunk in obj_body:
        first = True
        for s in chunk.split('\n'):
            if first:
                first = False
            else:
                yield linerem
                linerem = ''
            linerem += s
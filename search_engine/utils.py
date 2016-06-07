import bz2

def compress_data(data):
    if type(data) is not bytes:
        try:
            data = data.encode('utf-8')
        except Exception as err:
            print('Encode fail, error: ', err)

    return data


def decompress_data(data):
    return bz2.decompress(data)

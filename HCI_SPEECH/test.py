import os

base_dir = './imgs'

for fname in os.listdir(base_dir):
    if fname.split('.')[-1] == 'jpg':
        full_name = os.path.join(base_dir, fname)
        print(full_name)

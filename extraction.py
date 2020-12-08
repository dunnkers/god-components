import os
from time import time
import pandas

# Settings
KEY = os.environ.get('DESIGNITE_ENTERPRISE')
RUNTIME_JAR = 'designite/DesigniteJava_Enterprise.jar'
INPUT_FOLDER = '../tika'
OUTPUT_FOLDER = 'designite/report'
# Vars
jar = 'java -jar {}'.format(RUNTIME_JAR)

# We require a license key
if (not KEY): exit('No Designite Enterprise key! See README to configure.')
# Register license if not registered yet
if (not os.path.exists('designite/.config')):
    os.system('{} -r {}'.format(jar, KEY))

# Run Designite
start = time()
cmd = '{} -i {} -o {}'.format(jar, INPUT_FOLDER, OUTPUT_FOLDER)
print('Executing `{}`...'.format(cmd))
os.system(cmd)
end = time()
print('Designite ran for {:.2f} seconds'.format(end - start))

# Store results in a big CSV file
archsmells = pandas.read_csv('designite/{}/ArchitectureSmells.csv'.format(
    OUTPUT_FOLDER))
godcomps = archsmells[archsmells['Architecture Smell'] == 'God Component'].copy()
tag = '2.0.0-SNAPSHOT'
godcomps['Tag'] = tag
godcompsfile = 'designite/godcomps.csv'
if (os.path.exists(godcompsfile)): # Merge existing 
    godcomps = pandas.concat([
        pandas.read_csv(godcompsfile),
        godcomps
    ])
godcomps.to_csv(godcompsfile, index=False)
print('end')
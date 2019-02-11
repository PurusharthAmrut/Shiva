import urllib.request
import re

lncount = 0
m2count = 0
m1count = 0
m3count = 0
m4count = 0
m5count = 0

objdict = {2:m2count, 3:m3count, 4: m4count, 5:m5count} #dictionary used for avoiding code redundancy

fhand=urllib.request.urlopen('https://sih.isro.gov.in/samples/P2/214_19FEB06_000002.GPS')     #encoding='utf-8' is very important for program to function
messagedictinverse=dict()
decode = {
    '0':'0000',
    '1':'0001',
    '2':'0010',
    '3':'0011',
    '4':'0100',
    '5':'0101',
    '6':'0110',
    '7':'0111',
    '8':'1000',
    '9':'1001',
    'a':'1010',
    'b':'1011',
    'c':'1100',
    'd':'1101',
    'e':'1110',
    'f':'1111'
}
messagedict = {2:'WAAS2A', 3:'WAAS3A', 4:'WAAS4A', 5:'WAAS5A'}
for key in messagedict:
    messagedictinverse['#'+messagedict[key]]=key

#This function increments m2count and prints Fast Corrections, and below them, the corresponding UDREIs
def interpretMessage2(line,messagenumber):
    print(messagedict[messagenumber])
    print(line)
    line=line.rstrip()

    global m2count, m3count, m4count, m5count
    objdict[messagenumber] = objdict[messagenumber]+1

    pos=line.find(';')          #Jumping across the header
    pos=line.find(',', pos)     #Jumping over "Source PRN of message" field
    iodf = line[pos+1:line.find(',', pos+1)]    #Next field is the IODF
    pos=line.find(',', pos+1)                           #Updating position to the next field
    iodp = line[pos+1:line.find(',', pos+1)]            #Next field id the IODP
    pos=line.find(',', pos+1)                           #Updating position to the next field
    prcf=re.findall(',(-*[0-9]+)', line[pos:])          #Extracting all fast corrections and UDREIs

    print('IODF:'+iodf)
    print('IODP:'+iodp)
    print("Fast corrections")
    for i in range(13):                                 #First 13 field belong to Fast corrections
        x=int(prcf[i])*0.125
        print(x, end=',')
    print()
    print("UDREI")
    for i in range(13,26):                               #Next 13 fields are the UDREIs corresponding to each fast correction
        print(prcf[i], end=',')
    print('\n')

    #Error handling section:
    if len(prcf)!=26:
        print(line)
        print('Unexpected length of Fast corrections or UDREIs')
        return 0

    if len(iodp)!=1 or len(iodf)!=1:
        print(line)
        print('unexpected length of iodp or iodf')
        return 0

#This function increments m1count,
def interpretMessage1(line):
    print('WAAS1A')
    line = line.rstrip()

    global m1count
    m1count = m1count + 1

    pos=line.find(';')
    pos=line.find(',', pos)
    PRNbits = re.findall('[a-z0-9]', line[pos+1:line.find(',', pos+1)])
    pos=line.find(',', pos+1)
    iodp=re.findall('[0-3]', line[pos:])

    print('IODP:'+iodp[0])
    for byte in PRNbits:
        print(decode[byte], end='')
    print()

    if len(PRNbits)!=54:
        print('PRN bit mask length not equal to 54')
        return 0

#It must be noted that some of the error line also contain # at the begining. This is rare, but it does exist.
def extract(fileHandle):
    global lncount, m2count
    for codedline in fileHandle:
        lncount = lncount + 1                   #Remember to cross check this with the total number of line in the file (for testing purposes)
        if not codedline.startswith(b'#WAAS'):  #Remember, right now I have ignored RXCONFIG AND RAWEPHEMA. Only dealing with required details
            continue
        line=codedline.decode('utf-8')
        if line[:7] in messagedictinverse:                                #if re.search('^#WAAS2A', line)
            if interpretMessage2(line,messagedictinverse[line[:7]])==0:
                print("PROGRAM TERMINATING.....")
                quit()
        elif line.startswith('#WAAS1A'):
            if interpretMessage1(line)==0:
                print("PROGRAM TERMINATING.....")
                quit()

try:
    extract(fhand)
finally:
    fhand.close()
    print("\n\nNumber of lines searched:",lncount)
    print("Number of messages of type 1:",m1count)
    for num in objdict:                             #Again, using dictionary to reduce code redundancy
        print("Number of messages of type",num,":",objdict[num])

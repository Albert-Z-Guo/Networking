commit_list = []
with open('log/TestReliableWithoutLossWithoutCorruptAtScale_test_send_many_pkt.txt', 'r') as f:
    for line in f:
        commit_list.append(line) 

send_list = []
with open('log/send_list.txt', 'r') as f2:          
    for line in f2:
        send_list.append(line)


for i in range(len(commit_list)):
    if commit_list[i] != send_list[i]:
        print(i, commit_list[i].strip(), send_list[i])

        commit_bytearray = bytearray(eval(commit_list[i][10:-2]))
        print(commit_bytearray[:2], commit_bytearray[2:-2], commit_bytearray[-2:])
        print(sum(commit_bytearray[:-2]), int.from_bytes(commit_bytearray[-2:], byteorder='big')) # check checksum
        
        send_bytearray = bytearray(eval(send_list[i][10:-2]))
        print(send_bytearray[:2], send_bytearray[2:-2], send_bytearray[-2:])
        print(sum(send_bytearray[:-2]), int.from_bytes(send_bytearray[-2:], byteorder='big')) # check checksum
        print('')

print(set(commit_list) - set(send_list))
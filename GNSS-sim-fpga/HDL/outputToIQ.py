with open('output_results.txt', 'r') as result_file:
    with open("signal.sigmf-data", 'wb') as iq_file:
        n = 0
        for line in result_file:
            n+=1
            [i, q] = line.split(", ")
            
            i = int(i)
            if i==-1:
              i=0
            if i==1:
              i=0
            if i<0:
                i += 256
            i = i.to_bytes(1)
            iq_file.write(i)
            
            q = int(q)
            if q==-1:
              q=0
            if q==1:
              q=0
            if q<0:
                q += 256
            q = q.to_bytes(1)
            iq_file.write(q)
        print("n:", n)
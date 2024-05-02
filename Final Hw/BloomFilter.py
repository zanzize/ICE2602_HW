from Bitarray import Bitarray
import math

class BloomFilter():
    
    def __init__(self,size,error_rate):
        
        self.n = size
        self.m = int(-int(size)*math.log(error_rate)/(math.log(2)**2))
        self.k = int(self.m/self.n*math.log(2))
        self.storage = Bitarray(self.m)
        
    def hash_values(self,key):
        
        def BKDRHash(seed,key):
            hash = 0
            for i in range(len(key)):
                hash = (hash * seed)+ ord(key[i])
            return hash
        seeds = [131]
        values = list()
        for i in range(self.k-1):
            seeds.append(seeds[i]*100+31)
        for seed in seeds:
            values.append(BKDRHash(seed,key)%self.m)
        return values
    def __contains__(self,obj):
        for value in self.hash_values(obj):
            if not self.storage.get(value):
                return False
        return True
        
    def add(self,msg):
        for value in self.hash_values(msg):
            self.storage.set(value)

if __name__== "__main__":
        f = open('sjtu.txt')
        l = f.read().split()
        s= set()
        t = BloomFilter(len(l),0.2)
        error_counter = 0
        for word in l:
            if word not in s:
                if word in t:
                    error_counter +=1
                else:
                    t.add(word)
                s.add(word)
        print(error_counter/len(l))
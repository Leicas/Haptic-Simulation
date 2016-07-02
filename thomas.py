import multicom.com as com
i = 0
if __name__ == '__main__':
  PINCE = com.HDevice("COM7")
  PINCE.launch()
  while i < 100:
    data = PINCE.readsep(r'\|',4)[2]
    print(data)
    i+=1

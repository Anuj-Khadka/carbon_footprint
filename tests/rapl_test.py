import pyRAPL
pyRAPL.setup()
meter = pyRAPL.Measurement('test')
meter.begin()
x = sum(range(1000000))
meter.end()
print('RAPL OK')
print(meter.result)
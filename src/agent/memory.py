from mem0 import Memory

memory = None
try:
    memory = Memory()
except Exception as e:
    print(e)
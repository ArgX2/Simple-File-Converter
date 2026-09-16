"""In-memory registry API for tests when HKCU writes are sandbox-blocked."""
class Key:
    def __init__(self, store, path): self.store,self.path=store,path
    def __enter__(self): return self
    def __exit__(self,*args): pass
class Registry:
    HKEY_CURRENT_USER=1
    KEY_WRITE=2
    KEY_READ=1
    REG_SZ=1
    def __init__(self): self.data={}
    def CreateKeyEx(self, hive, path, reserved=0, access=0):
        parts=path.split('\\')
        for i in range(1,len(parts)+1): self.data.setdefault('\\'.join(parts[:i]),{})
        return Key(self,path)
    def OpenKey(self,hive,path,reserved=0,access=0):
        if path not in self.data: raise FileNotFoundError(path)
        return Key(self,path)
    def SetValueEx(self,key,name,reserved,kind,value): self.data[key.path][name]=(value,kind)
    def QueryValueEx(self,key,name):
        if name not in self.data[key.path]: raise FileNotFoundError(name)
        return self.data[key.path][name]
    def children(self,path):
        return sorted(p[len(path)+1:] for p in self.data if p.startswith(path+'\\') and '\\' not in p[len(path)+1:])
    def QueryInfoKey(self,key): return len(self.children(key.path)),len(self.data[key.path]),0
    def EnumKey(self,key,index): return self.children(key.path)[index]
    def DeleteKey(self,hive,path):
        if path not in self.data: raise FileNotFoundError(path)
        assert not self.children(path)
        del self.data[path]
